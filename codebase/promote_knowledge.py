"""Validate human review decisions and promote approved FAQ entries atomically."""

from __future__ import annotations

import csv
from datetime import date
import json
from pathlib import Path
import re
from typing import Any

from knowledge_base import load_approved_knowledge


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_QUEUE_PATH = (
    REPO_ROOT / "data" / "processed" / "discord" / "review-queue.csv"
)
DEFAULT_CANDIDATES_PATH = (
    REPO_ROOT / "data" / "processed" / "discord" / "qa-candidates.csv"
)
DEFAULT_OUTPUT_PATH = (
    REPO_ROOT / "data" / "approved" / "course-knowledge.json"
)
ALLOWED_DECISIONS = {"approved", "rejected", "needs_clarification"}
SOURCE_ID_PATTERN = re.compile(r"^IMG-\d{3}$")
SENSITIVE_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"\bAIza[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{8,}", re.IGNORECASE),
    re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"(?<!\d)(?:\+?84|0)\d{8,10}(?!\d)"),
    re.compile(r"(?<!\d)\d{15,20}(?!\d)"),
    re.compile(r"\b\d{10,}_[^\s]+\.jpe?g\b", re.IGNORECASE),
    re.compile(
        r"\b(?:password|mật\s*khẩu|secret|token|api[_ -]?key)\b"
        r"\s*[:=]\s*\S+",
        re.IGNORECASE,
    ),
)


class PromotionValidationError(ValueError):
    """Raised when reviewed data is unsafe or incomplete."""


def _read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8", newline="") as source:
            return list(csv.DictReader(source))
    except (OSError, UnicodeError, csv.Error) as error:
        raise PromotionValidationError(f"Cannot read review input: {path.name}") from error


def _required(row: dict[str, str], field: str, candidate_id: str) -> str:
    value = (row.get(field) or "").strip()
    if not value:
        raise PromotionValidationError(
            f"{candidate_id}: missing required field {field}"
        )
    return value


def _safe_text(value: str, candidate_id: str) -> str:
    if any(pattern.search(value) for pattern in SENSITIVE_PATTERNS):
        raise PromotionValidationError(
            f"{candidate_id}: corrected data contains PII or a secret"
        )
    return value.strip()


def _parse_json_list(value: str, field: str, candidate_id: str) -> list[str]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as error:
        raise PromotionValidationError(
            f"{candidate_id}: invalid JSON in {field}"
        ) from error
    if not isinstance(parsed, list) or not all(
        isinstance(item, str) and item.strip() for item in parsed
    ):
        raise PromotionValidationError(
            f"{candidate_id}: {field} must be a non-empty string list"
        )
    return [item.strip() for item in parsed]


def promote_approved_knowledge(
    queue_path: str | Path = DEFAULT_QUEUE_PATH,
    candidates_path: str | Path = DEFAULT_CANDIDATES_PATH,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> dict[str, int]:
    """Promote only complete approved rows and return decision counts."""

    queue_rows = _read_csv(Path(queue_path))
    candidate_rows = _read_csv(Path(candidates_path))
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    if len(candidates) != len(candidate_rows):
        raise PromotionValidationError("Duplicate candidate_id in candidates CSV")

    promoted: list[dict[str, Any]] = []
    seen_questions: set[str] = set()
    counts = {"approved": 0, "expired": 0, "handoff": 0}

    for row in queue_rows:
        candidate_id = _required(row, "candidate_id", "unknown")
        decision = _required(row, "approval_decision", candidate_id)
        if decision not in ALLOWED_DECISIONS:
            raise PromotionValidationError(
                f"{candidate_id}: invalid approval_decision"
            )
        candidate = candidates.get(candidate_id)
        if candidate is None:
            raise PromotionValidationError(
                f"{candidate_id}: missing candidate source row"
            )

        reviewer = _required(row, "reviewer", candidate_id)
        reviewed_at = _required(row, "reviewed_at", candidate_id)
        try:
            reviewed_date = date.fromisoformat(reviewed_at)
        except ValueError as error:
            raise PromotionValidationError(
                f"{candidate_id}: reviewed_at must be YYYY-MM-DD"
            ) from error

        if decision != "approved":
            valid_until = (row.get("valid_until") or "").strip()
            if decision == "rejected" and valid_until:
                try:
                    expiry = date.fromisoformat(valid_until)
                except ValueError as error:
                    raise PromotionValidationError(
                        f"{candidate_id}: invalid expired valid_until"
                    ) from error
                if expiry < reviewed_date:
                    counts["expired"] += 1
                    continue
            counts["handoff"] += 1
            continue

        corrected_answer = _safe_text(
            _required(row, "corrected_answer", candidate_id),
            candidate_id,
        )
        official_source = _safe_text(
            _required(row, "official_source", candidate_id),
            candidate_id,
        )
        canonical_question = _safe_text(
            _required(candidate, "canonical_question", candidate_id),
            candidate_id,
        )
        question_key = canonical_question.casefold().strip()
        if question_key in seen_questions:
            raise PromotionValidationError(
                f"{candidate_id}: duplicate approved canonical question"
            )
        seen_questions.add(question_key)

        variants = [
            _safe_text(value, candidate_id)
            for value in _parse_json_list(
                candidate["question_variants"],
                "question_variants",
                candidate_id,
            )
        ]
        source_ids = _parse_json_list(
            candidate["source_image_ids"],
            "source_image_ids",
            candidate_id,
        )
        if not all(SOURCE_ID_PATTERN.fullmatch(value) for value in source_ids):
            raise PromotionValidationError(
                f"{candidate_id}: invalid or original source filename"
            )

        volatile = candidate["contains_volatile_information"].lower() == "true"
        valid_until: str | None = None
        if volatile:
            valid_until = _required(row, "valid_until", candidate_id)
            try:
                expiry = date.fromisoformat(valid_until)
            except ValueError as error:
                raise PromotionValidationError(
                    f"{candidate_id}: valid_until must be YYYY-MM-DD"
                ) from error
            if expiry < reviewed_date:
                raise PromotionValidationError(
                    f"{candidate_id}: approved knowledge is already expired"
                )

        promoted.append(
            {
                "id": f"KB-{candidate_id.removeprefix('FAQ-')}",
                "topic": _required(candidate, "topic", candidate_id),
                "canonical_question": canonical_question,
                "question_variants": variants,
                "answer": corrected_answer,
                "source_image_ids": source_ids,
                "source_type": "human_reviewed",
                "official_source": official_source,
                "authority": "verified",
                "volatile": volatile,
                "valid_until": valid_until,
                "status": "approved",
                "verified_by": reviewer,
                "verified_at": reviewed_at,
            }
        )
        counts["approved"] += 1

    if counts["approved"] + counts["expired"] + counts["handoff"] != len(
        queue_rows
    ):
        raise PromotionValidationError("Not all review rows were accounted for")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    payload = {"schema_version": "1.0", "entries": promoted}
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    review_dates = {
        date.fromisoformat(entry["verified_at"]) for entry in promoted
    }
    validation_date = min(review_dates) if review_dates else date.today()
    loaded = load_approved_knowledge(temporary, today=validation_date)
    if len(loaded) != len(promoted):
        temporary.unlink(missing_ok=True)
        raise PromotionValidationError(
            "Generated runtime file failed approved loader validation"
        )
    temporary.replace(output)
    return counts


if __name__ == "__main__":
    result = promote_approved_knowledge()
    print(
        "Promotion complete: "
        f"approved={result['approved']}, "
        f"expired={result['expired']}, "
        f"handoff={result['handoff']}"
    )
