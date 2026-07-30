"""Fail-safe loader and keyword retriever for human-approved knowledge only."""

from __future__ import annotations

from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
import unicodedata
from typing import Any, TypedDict


REPO_ROOT = Path(__file__).resolve().parent.parent
APPROVED_KNOWLEDGE_PATH = (
    REPO_ROOT / "data" / "approved" / "course-knowledge.json"
)
LABCOACH_APPROVED_KNOWLEDGE_PATH = (
    REPO_ROOT / "data" / "approved" / "labcoach-knowledge.json"
)

SOURCE_ID_PATTERN = re.compile(r"^(IMG-\d{3}|HO-[A-Za-z0-9]+)$")
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?84|0)\d{8,10}(?!\d)")
DISCORD_ID_PATTERN = re.compile(r"(?<!\d)\d{15,20}(?!\d)")
ORIGINAL_FILE_PATTERN = re.compile(r"\b\d{10,}_[^\s]+\.jpe?g\b", re.IGNORECASE)
WORD_PATTERN = re.compile(r"\w+", re.UNICODE)
STOPWORDS = {
    "anh",
    "ban",
    "cac",
    "cho",
    "co",
    "cua",
    "duoc",
    "em",
    "gi",
    "hoi",
    "khong",
    "la",
    "lam",
    "minh",
    "nao",
    "nhu",
    "the",
    "thi",
    "va",
}
GENERIC_ROUTING_TERMS = {
    "bao",
    "bat",
    "buoi",
    "can",
    "ca",
    "cho",
    "chung",
    "dau",
    "deadline",
    "dai",
    "dien",
    "dong",
    "duoc",
    "gian",
    "gio",
    "han",
    "hoc",
    "khi",
    "lich",
    "lop",
    "luc",
    "lau",
    "may",
    "ngay",
    "nao",
    "nop",
    "phai",
    "phut",
    "report",
    "team",
    "theo",
    "thang",
    "thong",
    "tin",
    "thoi",
    "tieng",
    "tiep",
    "trinh",
    "tuan",
    "chuong",
    "keo",
}
KB014_REQUIRED_ANCHORS = (
    "buoi toi",
    "toi",
    "online",
    "workshop",
    "office hour",
    "officehour",
    "mentor duty",
    "mentorduty",
    "lich hoat dong",
    "hoat dong",
    "theo tuan",
)
PHRASE_ALIASES = (
    (re.compile(r"\bbuild[\s_-]+phase\b"), " buildphase "),
    (re.compile(r"\b(?:mot nguoi|thanh vien)\b"), " thanhvien "),
    (re.compile(r"\bbao cao tuan\b"), " weekly report "),
    (re.compile(r"\bmentor duty\b"), " mentorduty "),
)
BUILD_PHASE_QUERY_SIGNALS = (
    "buildphase",
    "giai doan build",
    "chuong trinh build",
)


class KnowledgeMatch(TypedDict):
    knowledge_id: str
    source_ids: list[str]
    topic: str
    source_verified: bool
    answer: str


def _plain_text(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value.casefold())
    plain = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    for pattern, replacement in PHRASE_ALIASES:
        plain = pattern.sub(replacement, plain)
    return re.sub(r"\s+", " ", plain).strip()


def _contains_pii(value: str) -> bool:
    return any(
        pattern.search(value)
        for pattern in (
            EMAIL_PATTERN,
            PHONE_PATTERN,
            DISCORD_ID_PATTERN,
            ORIGINAL_FILE_PATTERN,
        )
    )


def _valid_until_is_current(value: object, today: date) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.date() >= today
    except ValueError:
        try:
            return date.fromisoformat(value) >= today
        except ValueError:
            return False


def _validate_entry(entry: object, today: date) -> dict[str, Any] | None:
    if not isinstance(entry, dict):
        return None
    base_fields = {
        "id",
        "topic",
        "canonical_question",
        "question_variants",
        "answer",
        "source_type",
        "authority",
        "volatile",
        "valid_until",
        "status",
        "verified_by",
        "verified_at",
    }
    if not base_fields.issubset(entry):
        return None

    if "source_ids" not in entry and "source_image_ids" not in entry:
        return None

    if entry.get("status") != "approved":
        return None
    if entry.get("authority") != "verified":
        return None
    if not isinstance(entry.get("id"), str) or not entry["id"].strip():
        return None
    if not isinstance(entry.get("topic"), str) or not entry["topic"].strip():
        return None
    if (
        not isinstance(entry.get("canonical_question"), str)
        or not entry["canonical_question"].strip()
    ):
        return None
    if not isinstance(entry.get("question_variants"), list) or not all(
        isinstance(value, str) and value.strip()
        for value in entry["question_variants"]
    ):
        return None
    if not isinstance(entry.get("answer"), str) or not entry["answer"].strip():
        return None

    # Validate provenance from source_ids or source_image_ids
    src_ids = entry.get("source_ids")
    if src_ids is None:
        src_ids = entry.get("source_image_ids")

    if not isinstance(src_ids, list) or not src_ids:
        return None
    if not all(
        isinstance(value, str) and SOURCE_ID_PATTERN.fullmatch(value)
        for value in src_ids
    ):
        return None

    if not isinstance(entry.get("volatile"), bool):
        return None
    if entry["volatile"] and not _valid_until_is_current(
        entry.get("valid_until"),
        today,
    ):
        return None
    if (
        not isinstance(entry.get("verified_by"), str)
        or not entry["verified_by"].strip()
        or not isinstance(entry.get("verified_at"), str)
        or not entry["verified_at"].strip()
    ):
        return None

    public_text = " ".join(
        [
            entry["canonical_question"],
            *entry["question_variants"],
            entry["answer"],
        ]
    )
    if _contains_pii(public_text):
        return None

    normalized = dict(entry)
    normalized["source_ids"] = list(src_ids)
    if "source_image_ids" in normalized:
        normalized["source_image_ids"] = list(src_ids)
    return normalized


def _read_json_file(path: Path) -> list[dict[str, Any]]:
    """Safely read and parse entries list from a JSON file."""
    try:
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        if (
            isinstance(payload, dict)
            and payload.get("schema_version") == "1.0"
            and isinstance(payload.get("entries"), list)
        ):
            return payload["entries"]
    except (OSError, json.JSONDecodeError, UnicodeError):
        pass
    return []


def load_approved_knowledge(
    path: str | Path | None = None,
    *,
    today: date | None = None,
) -> list[dict[str, Any]]:
    """Load valid approved entries from course and labcoach knowledge files."""
    if path is not None:
        raw_entries = _read_json_file(Path(path))
    else:
        course_entries = _read_json_file(APPROVED_KNOWLEDGE_PATH)
        labcoach_entries = _read_json_file(LABCOACH_APPROVED_KNOWLEDGE_PATH)
        raw_entries = course_entries + labcoach_entries

    current_date = today or datetime.now(timezone.utc).date()
    approved: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_questions: set[str] = set()
    for raw_entry in raw_entries:
        entry = _validate_entry(raw_entry, current_date)
        if entry is None:
            continue
        normalized_question = _plain_text(entry["canonical_question"]).strip()
        if entry["id"] in seen_ids or normalized_question in seen_questions:
            continue
        seen_ids.add(entry["id"])
        seen_questions.add(normalized_question)
        approved.append(entry)
    return approved


def _keywords(value: str) -> set[str]:
    return {
        token
        for token in WORD_PATTERN.findall(_plain_text(value))
        if len(token) >= 3 and token not in STOPWORDS
    }


def _codes(value: str) -> set[str]:
    return {
        token
        for token in WORD_PATTERN.findall(_plain_text(value))
        if any(character.isdigit() for character in token)
    }


def retrieve_approved_match(
    question: str,
    path: str | Path | None = None,
    *,
    today: date | None = None,
) -> KnowledgeMatch | None:
    """Return one confidently matched approved source or ``None``."""
    question_tokens = _keywords(question)
    if not question_tokens:
        return None
    question_codes = _codes(question)
    normalized_question = _plain_text(question)

    candidates: list[tuple[float, dict[str, Any]]] = []
    for entry in load_approved_knowledge(path, today=today):
        if entry["id"] == "KB-014" and not any(
            anchor in normalized_question for anchor in KB014_REQUIRED_ANCHORS
        ):
            continue
        searchable = " ".join(
            [
                entry["canonical_question"],
                *entry["question_variants"],
                entry["topic"],
                entry["answer"],
            ]
        )
        normalized_searchable = _plain_text(searchable)
        if (
            "buildphase" in normalized_searchable
            and not any(
                signal in normalized_question
                for signal in BUILD_PHASE_QUERY_SIGNALS
            )
        ):
            continue
        entry_tokens = _keywords(searchable)
        overlap = question_tokens.intersection(entry_tokens)
        anchors = overlap.difference(GENERIC_ROUTING_TERMS)
        if not anchors:
            continue
        if question_codes and not question_codes.issubset(_codes(searchable)):
            continue

        exact_anchor = any(
            len(token) >= 5 and token in normalized_searchable
            for token in anchors
        )
        if len(anchors) < 2 and not exact_anchor:
            continue

        coverage = len(overlap) / max(1, len(question_tokens))
        anchor_coverage = len(anchors) / max(
            1,
            len(question_tokens.difference(GENERIC_ROUTING_TERMS)),
        )
        phrase_bonus = 1.0 if normalized_question in normalized_searchable else 0.0
        score = (
            len(anchors) * 3.0
            + len(overlap)
            + coverage * 2.0
            + anchor_coverage * 2.0
            + phrase_bonus
        )
        candidates.append((score, entry))

    if not candidates:
        return None

    candidates.sort(key=lambda item: (-item[0], item[1]["id"]))
    best_score, best_entry = candidates[0]
    if len(candidates) > 1 and best_score - candidates[1][0] < 1.0:
        return None

    src_ids = best_entry.get("source_ids") or best_entry.get("source_image_ids") or []
    return KnowledgeMatch(
        knowledge_id=best_entry["id"],
        source_ids=list(src_ids),
        topic=best_entry["topic"],
        source_verified=True,
        answer=best_entry["answer"],
    )


def knowledge_match_to_context(match: KnowledgeMatch | None) -> str | None:
    """Serialize a structured match as prompt data."""
    if match is None:
        return None
    return json.dumps(
        {
            "answer": match["answer"],
            "source_ids": match["source_ids"],
            "knowledge_id": match["knowledge_id"],
            "topic": match["topic"],
            "source_verified": match["source_verified"],
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )


def retrieve_approved_context(
    question: str,
    path: str | Path | None = None,
    *,
    today: date | None = None,
) -> str | None:
    """Compatibility wrapper returning serialized approved context."""
    return knowledge_match_to_context(
        retrieve_approved_match(question, path, today=today)
    )
