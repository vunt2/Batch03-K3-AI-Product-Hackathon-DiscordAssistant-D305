"""SQLite persistence store for learner assistant handoff queue."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3
from typing import Any
import uuid

from conversation_context import redact_sensitive_text


CODEBASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = CODEBASE_DIR.parent
DEFAULT_DB_PATH = REPO_ROOT / "data" / "runtime" / "assistant.db"

PENDING = "pending"
RESOLVED = "resolved"
VALID_STATUSES = (PENDING, RESOLVED)

PENDING_REVIEW = "pending_review"
APPROVED_FOR_PUBLISH = "approved_for_publish"
REJECTED = "rejected"
PUBLISHED = "published"
VALID_REVIEW_DECISIONS = (APPROVED_FOR_PUBLISH, REJECTED)


class StoreError(Exception):
    """Application exception for handoff store failures."""


def resolve_db_path(db_path: str | Path | None = None) -> Path:
    """Resolve absolute database file path, honoring ASSISTANT_DB_PATH env var."""
    if db_path is not None:
        target = Path(db_path)
    else:
        env_path = os.getenv("ASSISTANT_DB_PATH")
        if env_path and env_path.strip():
            target = Path(env_path.strip())
        else:
            target = DEFAULT_DB_PATH

    if not target.is_absolute():
        target = REPO_ROOT / target

    return target.resolve()


@contextmanager
def _connection(db_path: Path):
    """Context manager ensuring sqlite connection is closed and committed/rolled back."""
    conn = None
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        yield conn
        conn.commit()
    except sqlite3.Error as error:
        if conn is not None:
            try:
                conn.rollback()
            except sqlite3.Error:
                pass
        raise StoreError(f"Không thể truy cập kho handoff.") from error
    finally:
        if conn is not None:
            conn.close()


def initialize_store(db_path: str | Path | None = None) -> Path:
    """Initialize handoff table schema and indexes if they do not exist."""
    path = resolve_db_path(db_path)
    with _connection(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS handoffs (
                handoff_id TEXT PRIMARY KEY,
                learner_session_id TEXT NOT NULL,
                question TEXT NOT NULL,
                normalized_question TEXT NOT NULL,
                intent TEXT NOT NULL,
                reason TEXT NOT NULL,
                trace_id TEXT NOT NULL,
                model TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('pending', 'resolved')),
                labcoach_response TEXT NOT NULL DEFAULT '',
                resolved_at TEXT,
                updated_at TEXT NOT NULL
            );
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_handoffs_status ON handoffs(status);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_handoffs_session ON handoffs(learner_session_id);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_handoffs_created ON handoffs(created_at);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_handoffs_trace ON handoffs(trace_id);"
        )

        # Partial unique indexes for concurrency-safe deduplication
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uidx_handoffs_trace
            ON handoffs(trace_id)
            WHERE trace_id <> '';
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uidx_handoffs_pending_session_question
            ON handoffs(learner_session_id, normalized_question)
            WHERE status = 'pending';
            """
        )

        # Knowledge candidates table for Labcoach responses
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_candidates (
                candidate_id TEXT PRIMARY KEY,
                handoff_id TEXT NOT NULL UNIQUE,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                intent TEXT NOT NULL,
                source_type TEXT NOT NULL,
                review_status TEXT NOT NULL,
                reviewed_by TEXT NOT NULL DEFAULT '',
                reviewed_at TEXT,
                review_note TEXT NOT NULL DEFAULT '',
                published_knowledge_id TEXT NOT NULL DEFAULT '',
                published_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )

        # Idempotent migration for existing database instances
        cur_cols = conn.execute("PRAGMA table_info(knowledge_candidates);").fetchall()
        existing_cols = {col["name"] for col in cur_cols}

        if "reviewed_by" not in existing_cols:
            conn.execute(
                "ALTER TABLE knowledge_candidates ADD COLUMN reviewed_by TEXT NOT NULL DEFAULT '';"
            )
        if "reviewed_at" not in existing_cols:
            conn.execute(
                "ALTER TABLE knowledge_candidates ADD COLUMN reviewed_at TEXT;"
            )
        if "review_note" not in existing_cols:
            conn.execute(
                "ALTER TABLE knowledge_candidates ADD COLUMN review_note TEXT NOT NULL DEFAULT '';"
            )
        if "published_knowledge_id" not in existing_cols:
            conn.execute(
                "ALTER TABLE knowledge_candidates ADD COLUMN published_knowledge_id TEXT NOT NULL DEFAULT '';"
            )
        if "published_at" not in existing_cols:
            conn.execute(
                "ALTER TABLE knowledge_candidates ADD COLUMN published_at TEXT;"
            )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_candidates_status
            ON knowledge_candidates(review_status);
            """
        )
    return path


def _normalize_question(question: str) -> str:
    return " ".join(question.strip().casefold().split())


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "handoff_id": row["handoff_id"],
        "learner_session_id": row["learner_session_id"],
        "question": row["question"],
        "normalized_question": row["normalized_question"],
        "intent": row["intent"],
        "reason": row["reason"],
        "trace_id": row["trace_id"],
        "model": row["model"],
        "created_at": row["created_at"],
        "status": row["status"],
        "labcoach_response": row["labcoach_response"],
        "resolved_at": row["resolved_at"],
        "updated_at": row["updated_at"],
    }


def _candidate_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    keys = row.keys()
    return {
        "candidate_id": row["candidate_id"],
        "handoff_id": row["handoff_id"],
        "question": row["question"],
        "answer": row["answer"],
        "intent": row["intent"],
        "source_type": row["source_type"],
        "review_status": row["review_status"],
        "reviewed_by": row["reviewed_by"] if "reviewed_by" in keys else "",
        "reviewed_at": row["reviewed_at"] if "reviewed_at" in keys else None,
        "review_note": row["review_note"] if "review_note" in keys else "",
        "published_knowledge_id": row["published_knowledge_id"] if "published_knowledge_id" in keys else "",
        "published_at": row["published_at"] if "published_at" in keys else None,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def create_handoff(
    question: str,
    intent: str,
    reason: str,
    trace_id: str,
    model: str,
    learner_session_id: str,
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    """Create a new handoff record or return existing matching record."""
    if not isinstance(question, str) or not question.strip():
        raise StoreError("Câu hỏi handoff không được để trống.")
    if not isinstance(learner_session_id, str) or not learner_session_id.strip():
        raise StoreError("Session ID không được để trống.")
    if not isinstance(intent, str) or not isinstance(reason, str) or not isinstance(trace_id, str) or not isinstance(model, str):
        raise StoreError("Thông tin handoff không hợp lệ.")

    path = resolve_db_path(db_path)
    initialize_store(path)
    clean_q = question.strip()
    norm_q = _normalize_question(clean_q)
    now_iso = datetime.now(timezone.utc).isoformat()

    # Pre-check existing matching record
    existing = _find_existing_handoff(path, learner_session_id, norm_q, trace_id)
    if existing:
        return existing

    handoff_id = f"HO-{uuid.uuid4().hex[:8].upper()}"
    try:
        with _connection(path) as conn:
            conn.execute(
                """
                INSERT INTO handoffs (
                    handoff_id, learner_session_id, question, normalized_question,
                    intent, reason, trace_id, model, created_at, status,
                    labcoach_response, resolved_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    handoff_id,
                    learner_session_id,
                    clean_q,
                    norm_q,
                    intent,
                    reason,
                    trace_id,
                    model,
                    now_iso,
                    PENDING,
                    "",
                    None,
                    now_iso,
                ),
            )
    except StoreError:
        # Concurrent insertion conflict handling: query existing record
        dup = _find_existing_handoff(path, learner_session_id, norm_q, trace_id)
        if dup:
            return dup
        raise

    loaded = get_handoff(handoff_id, db_path=path)
    if loaded:
        return loaded
    raise StoreError("Không thể lưu yêu cầu handoff.")


def _find_existing_handoff(
    path: Path, learner_session_id: str, norm_q: str, trace_id: str
) -> dict[str, Any] | None:
    """Helper to query existing record by trace_id or pending session+question."""
    with _connection(path) as conn:
        if trace_id:
            cur = conn.execute(
                "SELECT * FROM handoffs WHERE trace_id = ? LIMIT 1;",
                (trace_id,),
            )
            row = cur.fetchone()
            if row:
                return _row_to_dict(row)

        cur = conn.execute(
            """
            SELECT * FROM handoffs
            WHERE learner_session_id = ?
              AND normalized_question = ?
              AND status = ?
            LIMIT 1;
            """,
            (learner_session_id, norm_q, PENDING),
        )
        row = cur.fetchone()
        if row:
            return _row_to_dict(row)
    return None


def list_handoffs(
    status: str | None = None, db_path: str | Path | None = None
) -> list[dict[str, Any]]:
    """List handoff records, optionally filtered by status."""
    path = resolve_db_path(db_path)
    initialize_store(path)
    with _connection(path) as conn:
        if status in VALID_STATUSES:
            cur = conn.execute(
                "SELECT * FROM handoffs WHERE status = ? ORDER BY created_at DESC;",
                (status,),
            )
        else:
            cur = conn.execute(
                "SELECT * FROM handoffs ORDER BY created_at DESC;"
            )
        return [_row_to_dict(r) for r in cur.fetchall()]


def get_handoff(
    handoff_id: str, db_path: str | Path | None = None
) -> dict[str, Any] | None:
    """Retrieve a single handoff record by ID."""
    path = resolve_db_path(db_path)
    initialize_store(path)
    with _connection(path) as conn:
        cur = conn.execute(
            "SELECT * FROM handoffs WHERE handoff_id = ?;", (handoff_id,)
        )
        row = cur.fetchone()
        return _row_to_dict(row) if row else None


def count_handoffs(
    db_path: str | Path | None = None,
) -> tuple[int, int]:
    """Return tuple of (pending_count, resolved_count)."""
    path = resolve_db_path(db_path)
    initialize_store(path)
    with _connection(path) as conn:
        cur_p = conn.execute(
            "SELECT COUNT(*) FROM handoffs WHERE status = ?;", (PENDING,)
        )
        pending = cur_p.fetchone()[0]
        cur_r = conn.execute(
            "SELECT COUNT(*) FROM handoffs WHERE status = ?;", (RESOLVED,)
        )
        resolved = cur_r.fetchone()[0]
        return pending, resolved


def resolve_handoff(
    handoff_id: str, response: str, db_path: str | Path | None = None
) -> bool:
    """Mark a handoff as resolved with Labcoach response and capture knowledge candidate."""
    if not isinstance(response, str):
        return False

    clean_resp = redact_sensitive_text(response.strip()).strip()
    if not clean_resp:
        return False

    path = resolve_db_path(db_path)
    initialize_store(path)
    now_iso = datetime.now(timezone.utc).isoformat()

    with _connection(path) as conn:
        cur = conn.execute(
            "SELECT question, intent FROM handoffs WHERE handoff_id = ?;",
            (handoff_id,),
        )
        row = cur.fetchone()
        if not row:
            return False

        clean_question = redact_sensitive_text(row["question"].strip()).strip()
        if not clean_question:
            return False

        intent = row["intent"]

        # 1. Update handoff status and labcoach_response
        conn.execute(
            """
            UPDATE handoffs
            SET status = ?,
                labcoach_response = ?,
                resolved_at = ?,
                updated_at = ?
            WHERE handoff_id = ?;
            """,
            (RESOLVED, clean_resp, now_iso, now_iso, handoff_id),
        )

        # 2. Upsert knowledge candidate
        cur_cand = conn.execute(
            "SELECT candidate_id FROM knowledge_candidates WHERE handoff_id = ?;",
            (handoff_id,),
        )
        cand_row = cur_cand.fetchone()
        if cand_row:
            conn.execute(
                """
                UPDATE knowledge_candidates
                SET answer = ?,
                    intent = ?,
                    review_status = ?,
                    reviewed_by = ?,
                    reviewed_at = NULL,
                    review_note = ?,
                    updated_at = ?
                WHERE handoff_id = ?;
                """,
                (clean_resp, intent, PENDING_REVIEW, "", "", now_iso, handoff_id),
            )
        else:
            candidate_id = f"KC-{uuid.uuid4().hex[:8].upper()}"
            conn.execute(
                """
                INSERT INTO knowledge_candidates (
                    candidate_id, handoff_id, question, answer,
                    intent, source_type, review_status, reviewed_by, reviewed_at,
                    review_note, published_knowledge_id, published_at, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    candidate_id,
                    handoff_id,
                    clean_question,
                    clean_resp,
                    intent,
                    "labcoach_response",
                    PENDING_REVIEW,
                    "",
                    None,
                    "",
                    "",
                    None,
                    now_iso,
                    now_iso,
                ),
            )
        return True


def reopen_handoff(
    handoff_id: str, db_path: str | Path | None = None
) -> bool:
    """Reopen a resolved handoff back to pending status."""
    path = resolve_db_path(db_path)
    initialize_store(path)
    now_iso = datetime.now(timezone.utc).isoformat()

    try:
        with _connection(path) as conn:
            cur = conn.execute(
                "SELECT status FROM handoffs WHERE handoff_id = ?;", (handoff_id,)
            )
            row = cur.fetchone()
            if not row:
                return False

            conn.execute(
                """
                UPDATE handoffs
                SET status = ?,
                    resolved_at = NULL,
                    updated_at = ?
                WHERE handoff_id = ?;
                """,
                (PENDING, now_iso, handoff_id),
            )
            return True
    except StoreError:
        return False


def list_session_handoffs(
    learner_session_id: str, db_path: str | Path | None = None
) -> list[dict[str, Any]]:
    """List all handoff records belonging to a specific learner_session_id."""
    if not learner_session_id:
        return []
    path = resolve_db_path(db_path)
    initialize_store(path)
    with _connection(path) as conn:
        cur = conn.execute(
            "SELECT * FROM handoffs WHERE learner_session_id = ? ORDER BY created_at ASC;",
            (learner_session_id,),
        )
        return [_row_to_dict(r) for r in cur.fetchall()]


def delete_session_handoffs(
    learner_session_id: str, db_path: str | Path | None = None
) -> int:
    """Delete handoff records belonging only to the specified learner_session_id."""
    if not learner_session_id:
        return 0
    path = resolve_db_path(db_path)
    initialize_store(path)
    with _connection(path) as conn:
        cur = conn.execute(
            "DELETE FROM handoffs WHERE learner_session_id = ?;",
            (learner_session_id,),
        )
        return cur.rowcount


def get_knowledge_candidate(
    candidate_id: str, db_path: str | Path | None = None
) -> dict[str, Any] | None:
    """Retrieve a single knowledge candidate record by candidate_id."""
    if not candidate_id:
        return None
    path = resolve_db_path(db_path)
    initialize_store(path)
    with _connection(path) as conn:
        cur = conn.execute(
            "SELECT * FROM knowledge_candidates WHERE candidate_id = ?;",
            (candidate_id,),
        )
        row = cur.fetchone()
        return _candidate_row_to_dict(row) if row else None


def get_knowledge_candidate_for_handoff(
    handoff_id: str, db_path: str | Path | None = None
) -> dict[str, Any] | None:
    """Retrieve a single knowledge candidate record by handoff_id."""
    if not handoff_id:
        return None
    path = resolve_db_path(db_path)
    initialize_store(path)
    with _connection(path) as conn:
        cur = conn.execute(
            "SELECT * FROM knowledge_candidates WHERE handoff_id = ?;",
            (handoff_id,),
        )
        row = cur.fetchone()
        return _candidate_row_to_dict(row) if row else None


def list_knowledge_candidates(
    review_status: str | None = None, db_path: str | Path | None = None
) -> list[dict[str, Any]]:
    """List knowledge candidate records, optionally filtered by review_status."""
    path = resolve_db_path(db_path)
    initialize_store(path)
    with _connection(path) as conn:
        if review_status:
            cur = conn.execute(
                "SELECT * FROM knowledge_candidates WHERE review_status = ? ORDER BY created_at DESC;",
                (review_status,),
            )
        else:
            cur = conn.execute(
                "SELECT * FROM knowledge_candidates ORDER BY created_at DESC;"
            )
        return [_candidate_row_to_dict(r) for r in cur.fetchall()]


def review_knowledge_candidate(
    candidate_id: str,
    decision: str,
    edited_question: str,
    edited_answer: str,
    reviewer: str,
    review_note: str = "",
    db_path: str | Path | None = None,
) -> bool:
    """Review a knowledge candidate (approve for publish or reject)."""
    if decision not in VALID_REVIEW_DECISIONS:
        return False
    if not isinstance(reviewer, str) or not reviewer.strip():
        return False
    if not isinstance(edited_question, str) or not isinstance(edited_answer, str):
        return False

    clean_q = redact_sensitive_text(edited_question.strip()).strip()
    clean_a = redact_sensitive_text(edited_answer.strip()).strip()
    clean_note = redact_sensitive_text(review_note.strip()).strip() if isinstance(review_note, str) and review_note.strip() else ""

    if not clean_q or not clean_a:
        return False

    path = resolve_db_path(db_path)
    initialize_store(path)
    now_iso = datetime.now(timezone.utc).isoformat()
    clean_reviewer = reviewer.strip()

    with _connection(path) as conn:
        cur = conn.execute(
            "SELECT candidate_id FROM knowledge_candidates WHERE candidate_id = ?;",
            (candidate_id,),
        )
        if not cur.fetchone():
            return False

        conn.execute(
            """
            UPDATE knowledge_candidates
            SET question = ?,
                answer = ?,
                review_status = ?,
                reviewed_by = ?,
                reviewed_at = ?,
                review_note = ?,
                updated_at = ?
            WHERE candidate_id = ?;
            """,
            (
                clean_q,
                clean_a,
                decision,
                clean_reviewer,
                now_iso,
                clean_note,
                now_iso,
                candidate_id,
            ),
        )
        return True


def mark_candidate_published(
    candidate_id: str,
    knowledge_id: str,
    db_path: str | Path | None = None,
) -> bool:
    """Mark candidate as published with assigned knowledge_id."""
    if not candidate_id or not knowledge_id:
        return False
    path = resolve_db_path(db_path)
    initialize_store(path)
    now_iso = datetime.now(timezone.utc).isoformat()

    with _connection(path) as conn:
        cur = conn.execute(
            "SELECT review_status, published_knowledge_id FROM knowledge_candidates WHERE candidate_id = ?;",
            (candidate_id,),
        )
        row = cur.fetchone()
        if not row:
            return False

        current_status = row["review_status"]
        current_pub_id = row["published_knowledge_id"]

        # Only succeed if status is approved_for_publish OR already published with same knowledge_id
        if current_status == APPROVED_FOR_PUBLISH or (
            current_status == PUBLISHED and current_pub_id == knowledge_id
        ):
            conn.execute(
                """
                UPDATE knowledge_candidates
                SET review_status = ?,
                    published_knowledge_id = ?,
                    published_at = ?,
                    updated_at = ?
                WHERE candidate_id = ?;
                """,
                (PUBLISHED, knowledge_id, now_iso, now_iso, candidate_id),
            )
            return True
        return False


def count_knowledge_candidates(
    db_path: str | Path | None = None,
) -> tuple[int, int, int]:
    """Return tuple of (pending_review_count, approved_for_publish_count, rejected_count)."""
    path = resolve_db_path(db_path)
    initialize_store(path)
    with _connection(path) as conn:
        cur_p = conn.execute(
            "SELECT COUNT(*) FROM knowledge_candidates WHERE review_status = ?;", (PENDING_REVIEW,)
        )
        p = cur_p.fetchone()[0]
        cur_a = conn.execute(
            "SELECT COUNT(*) FROM knowledge_candidates WHERE review_status = ?;", (APPROVED_FOR_PUBLISH,)
        )
        a = cur_a.fetchone()[0]
        cur_r = conn.execute(
            "SELECT COUNT(*) FROM knowledge_candidates WHERE review_status = ?;", (REJECTED,)
        )
        r = cur_r.fetchone()[0]
        return p, a, r
