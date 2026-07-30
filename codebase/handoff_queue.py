"""Session-scoped handoff queue helpers for the Streamlit demo."""

from __future__ import annotations

from datetime import datetime
import uuid
from typing import Any


PENDING = "pending"
RESOLVED = "resolved"


def enqueue_handoff(
    queue: list[dict[str, Any]],
    *,
    question: str,
    intent: str,
    reason: str,
    trace_id: str,
    model: str,
) -> str:
    """Add one handoff unless the same trace/question is already pending."""

    normalized_question = " ".join(question.casefold().split())
    for item in queue:
        if item["trace_id"] == trace_id:
            return str(item["handoff_id"])
        if (
            item["status"] == PENDING
            and " ".join(str(item["question"]).casefold().split())
            == normalized_question
        ):
            return str(item["handoff_id"])

    handoff_id = f"HO-{uuid.uuid4().hex[:8].upper()}"
    queue.append(
        {
            "handoff_id": handoff_id,
            "question": question,
            "intent": intent,
            "reason": reason,
            "trace_id": trace_id,
            "model": model,
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "status": PENDING,
            "labcoach_response": "",
            "resolved_at": None,
        }
    )
    return handoff_id


def resolve_handoff(
    queue: list[dict[str, Any]],
    handoff_id: str,
    response: str,
) -> bool:
    """Store a Labcoach response and resolve the matching item."""

    clean_response = response.strip()
    if not clean_response:
        return False
    for item in queue:
        if item["handoff_id"] == handoff_id:
            item["labcoach_response"] = clean_response
            item["status"] = RESOLVED
            item["resolved_at"] = datetime.now().astimezone().isoformat(
                timespec="seconds"
            )
            return True
    return False


def reopen_handoff(
    queue: list[dict[str, Any]],
    handoff_id: str,
) -> bool:
    """Move a resolved item back to the pending queue."""

    for item in queue:
        if item["handoff_id"] == handoff_id:
            item["status"] = PENDING
            item["resolved_at"] = None
            return True
    return False


def queue_counts(queue: list[dict[str, Any]]) -> tuple[int, int]:
    pending = sum(item["status"] == PENDING for item in queue)
    resolved = sum(item["status"] == RESOLVED for item in queue)
    return pending, resolved
