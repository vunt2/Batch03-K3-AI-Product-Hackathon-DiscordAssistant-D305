"""Module to publish approved knowledge candidates into labcoach-knowledge.json."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any
import unicodedata
import uuid

from handoff_store import (
    APPROVED_FOR_PUBLISH,
    PUBLISHED,
    StoreError,
    get_knowledge_candidate,
    mark_candidate_published,
)
from knowledge_base import load_approved_knowledge


CODEBASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = CODEBASE_DIR.parent
LABCOACH_KNOWLEDGE_PATH = REPO_ROOT / "data" / "approved" / "labcoach-knowledge.json"
COURSE_KNOWLEDGE_PATH = REPO_ROOT / "data" / "approved" / "course-knowledge.json"


class KnowledgePublishError(Exception):
    """Domain exception for knowledge publish failures."""


def _normalize_canonical_question(question: str) -> str:
    normalized = unicodedata.normalize("NFD", question.casefold())
    plain = "".join(char for char in normalized if not unicodedata.combining(char))
    plain = plain.replace("đ", "d")
    return re.sub(r"\s+", " ", plain).strip()


def publish_candidate(
    candidate_id: str,
    topic: str,
    volatile: bool,
    valid_until: str | None = None,
    knowledge_path: str | Path | None = None,
    db_path: str | Path | None = None,
    base_knowledge_path: str | Path | None = None,
) -> dict[str, Any]:
    """Publish an approved knowledge candidate to labcoach-knowledge.json atomically."""
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise KnowledgePublishError("ID candidate không hợp lệ.")

    # 1. Resolve paths and protect course knowledge
    target_path = Path(knowledge_path).resolve() if knowledge_path is not None else LABCOACH_KNOWLEDGE_PATH.resolve()
    base_path = Path(base_knowledge_path).resolve() if base_knowledge_path is not None else COURSE_KNOWLEDGE_PATH.resolve()

    if target_path == base_path or target_path == COURSE_KNOWLEDGE_PATH.resolve():
        raise KnowledgePublishError("Không được ghi đè file knowledge gốc của khóa học.")

    # 2. Query candidate
    try:
        cand = get_knowledge_candidate(candidate_id, db_path=db_path)
    except StoreError as error:
        raise KnowledgePublishError("Lỗi kết nối kho lưu trữ candidate.") from error

    if not cand:
        raise KnowledgePublishError("Không tìm thấy knowledge candidate.")

    if cand["review_status"] not in (APPROVED_FOR_PUBLISH, PUBLISHED):
        raise KnowledgePublishError("Candidate không ở trạng thái sẵn sàng publish.")

    if (
        not cand.get("question")
        or not cand.get("answer")
        or not cand.get("reviewed_by")
        or not cand.get("reviewed_at")
    ):
        raise KnowledgePublishError("Candidate thiếu thông tin review bắt buộc.")

    if not isinstance(topic, str) or not topic.strip():
        raise KnowledgePublishError("Topic không được để trống.")

    if not isinstance(volatile, bool):
        raise KnowledgePublishError("Trường volatile phải là kiểu boolean.")

    today_utc = datetime.now(timezone.utc).date()
    if volatile:
        if not isinstance(valid_until, str) or not valid_until.strip():
            raise KnowledgePublishError("Hàng volatile bắt buộc có thời hạn valid_until.")
        try:
            valid_until_date = datetime.strptime(valid_until.strip(), "%Y-%m-%d").date()
        except ValueError:
            raise KnowledgePublishError("Định dạng valid_until không đúng YYYY-MM-DD.")
        if valid_until_date < today_utc:
            raise KnowledgePublishError("Thời hạn valid_until không được trước ngày hiện tại.")
        final_valid_until = valid_until.strip()
    else:
        final_valid_until = None

    # Idempotent deterministic Knowledge ID mapping
    if candidate_id.startswith("KC-"):
        knowledge_id = f"KB-LC-{candidate_id[3:]}"
    else:
        knowledge_id = f"KB-LC-{candidate_id}"

    cand_norm_q = _normalize_canonical_question(cand["question"])

    # 3. Check base knowledge file for collisions
    base_entries: list[dict[str, Any]] = []
    if base_path.exists():
        try:
            raw_base = base_path.read_text(encoding="utf-8")
            base_data = json.loads(raw_base)
            if (
                not isinstance(base_data, dict)
                or base_data.get("schema_version") != "1.0"
                or not isinstance(base_data.get("entries"), list)
            ):
                raise KnowledgePublishError("File knowledge gốc không hợp lệ.")
            base_entries = base_data["entries"]
        except (OSError, json.JSONDecodeError, UnicodeError) as error:
            raise KnowledgePublishError("File knowledge gốc không hợp lệ.") from error

        for b_entry in base_entries:
            if isinstance(b_entry, dict) and b_entry.get("canonical_question"):
                if _normalize_canonical_question(b_entry["canonical_question"]) == cand_norm_q:
                    raise KnowledgePublishError("Câu hỏi trùng với knowledge gốc.")

    # 4. Check target knowledge file validity and existing entries
    existing_entries: list[dict[str, Any]] = []
    if target_path.exists():
        try:
            raw_target = target_path.read_text(encoding="utf-8")
            target_data = json.loads(raw_target)
            if (
                not isinstance(target_data, dict)
                or target_data.get("schema_version") != "1.0"
                or not isinstance(target_data.get("entries"), list)
            ):
                raise KnowledgePublishError("File target knowledge tồn tại nhưng không hợp lệ.")
            existing_entries = target_data["entries"]
        except (OSError, json.JSONDecodeError, UnicodeError) as error:
            raise KnowledgePublishError("File target knowledge tồn tại nhưng không hợp lệ.") from error

        for t_entry in existing_entries:
            if isinstance(t_entry, dict) and t_entry.get("canonical_question"):
                t_norm_q = _normalize_canonical_question(t_entry["canonical_question"])
                t_id = t_entry.get("id")
                if t_norm_q == cand_norm_q and t_id != knowledge_id:
                    raise KnowledgePublishError("Câu hỏi trùng với một entry khác trong target knowledge.")

    entry: dict[str, Any] = {
        "id": knowledge_id,
        "topic": topic.strip(),
        "canonical_question": cand["question"],
        "question_variants": [],
        "answer": cand["answer"],
        "source_ids": [cand["handoff_id"]],
        "source_type": "labcoach_reviewed",
        "official_source": "Labcoach persistent queue",
        "authority": "verified",
        "volatile": volatile,
        "valid_until": final_valid_until,
        "status": "approved",
        "verified_by": cand["reviewed_by"],
        "verified_at": cand["reviewed_at"],
    }

    # Update in-place or append
    entries_to_write = list(existing_entries)
    updated = False
    for idx, existing in enumerate(entries_to_write):
        if isinstance(existing, dict) and existing.get("id") == knowledge_id:
            entries_to_write[idx] = entry
            updated = True
            break
    if not updated:
        entries_to_write.append(entry)

    payload = {
        "schema_version": "1.0",
        "entries": entries_to_write,
    }

    target_path.parent.mkdir(parents=True, exist_ok=True)
    temp_file = target_path.parent / f".tmp_{uuid.uuid4().hex}_{target_path.name}"

    try:
        temp_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        # 5. Validate temp file with load_approved_knowledge before replace
        loaded = load_approved_knowledge(temp_file)
        if not any(e.get("id") == knowledge_id for e in loaded):
            raise KnowledgePublishError("Payload không vượt qua kiểm tra của loader.")

        temp_file.replace(target_path)
    except Exception as error:
        if temp_file.exists():
            try:
                temp_file.unlink()
            except OSError:
                pass
        if isinstance(error, KnowledgePublishError):
            raise
        raise KnowledgePublishError("Không thể ghi file knowledge chính thức.") from error

    # 6. Mark candidate published in DB
    try:
        marked = mark_candidate_published(candidate_id, knowledge_id, db_path=db_path)
        if not marked:
            raise KnowledgePublishError("Không thể cập nhật trạng thái candidate thành published.")
    except StoreError as error:
        raise KnowledgePublishError("Lỗi kết nối kho lưu trữ khi đánh dấu published.") from error

    return entry
