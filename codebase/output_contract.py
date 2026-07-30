"""Validate and safely normalize CP3 model output before it reaches the UI."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Final, TypedDict, cast


VALID_INTENTS: Final[frozenset[str]] = frozenset(
    {"greeting", "learning", "logistics", "ambiguous", "out_of_scope"}
)
VALID_ACTIONS: Final[frozenset[str]] = frozenset(
    {
        "answer_briefly",
        "answer_with_guidance",
        "ask_clarifying_question",
        "handoff_to_ta",
        "decline_and_redirect",
    }
)
REQUIRED_FIELDS: Final[frozenset[str]] = frozenset(
    {"intent", "confidence", "action", "reply", "rationale"}
)
LOW_CONFIDENCE_THRESHOLD: Final[float] = 0.70
LOW_CONFIDENCE_ACTIONS: Final[frozenset[str]] = frozenset(
    {"ask_clarifying_question", "handoff_to_ta"}
)

_URL_PATTERN = re.compile(r"(?:https?://|www\.|discord\.gg/)\S+", re.IGNORECASE)
_CONCRETE_LOGISTICS_PATTERN = re.compile(
    r"(?:"
    r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b|"
    r"\b\d{4}-\d{2}-\d{2}\b|"
    r"\b\d{1,2}(?::\d{2})?\s*(?:am|pm|giờ)\b|"
    r"\b(?:thứ\s*(?:hai|ba|tư|năm|sáu|bảy)|chủ\s*nhật)\b|"
    r"\b(?:deadline|hạn\s*nộp|lịch\s*học)\s+(?:là|vào|lúc)\b"
    r")",
    re.IGNORECASE,
)


class ModelOutput(TypedDict):
    intent: str
    confidence: float
    action: str
    reply: str
    rationale: str


def _safe_fallback(reason: str, *, logistics: bool = False) -> ModelOutput:
    if logistics:
        return {
            "intent": "logistics",
            "confidence": 0.0,
            "action": "handoff_to_ta",
            "reply": (
                "Mình chưa có nguồn chính thức để xác nhận thông tin này. "
                "Mình sẽ chuyển câu hỏi cho TA hỗ trợ."
            ),
            "rationale": f"Fallback an toàn: {reason}",
        }
    return {
        "intent": "ambiguous",
        "confidence": 0.0,
        "action": "ask_clarifying_question",
        "reply": (
            "Mình chưa thể xử lý câu trả lời một cách an toàn. "
            "Bạn có thể nói rõ câu hỏi hoặc nội dung cần hỗ trợ không?"
        ),
        "rationale": f"Fallback an toàn: {reason}",
    }


def _looks_like_ungrounded_logistics(reply: str) -> bool:
    return bool(
        _URL_PATTERN.search(reply) or _CONCRETE_LOGISTICS_PATTERN.search(reply)
    )


def validate_model_output(
    raw_output: str | Mapping[str, object] | None,
    *,
    has_verified_logistics_source: bool = False,
) -> ModelOutput:
    """Return a display-safe model output, falling back on every contract error.

    ``has_verified_logistics_source`` must only be true when the application
    supplied an approved source relevant to the current logistics question.
    """

    if raw_output is None or (isinstance(raw_output, str) and not raw_output.strip()):
        return _safe_fallback("output rỗng")

    if isinstance(raw_output, str):
        try:
            parsed = json.loads(raw_output)
        except (json.JSONDecodeError, TypeError):
            return _safe_fallback("output không phải JSON hợp lệ")
    elif isinstance(raw_output, Mapping):
        parsed = dict(raw_output)
    else:
        return _safe_fallback("kiểu output không được hỗ trợ")

    if not isinstance(parsed, dict):
        return _safe_fallback("JSON phải là một object")

    missing_fields = REQUIRED_FIELDS.difference(parsed)
    if missing_fields:
        return _safe_fallback(
            "thiếu trường bắt buộc: " + ", ".join(sorted(missing_fields))
        )

    intent = parsed["intent"]
    action = parsed["action"]
    confidence = parsed["confidence"]
    reply = parsed["reply"]
    rationale = parsed["rationale"]

    if not isinstance(intent, str) or intent not in VALID_INTENTS:
        return _safe_fallback("intent không hợp lệ")
    is_logistics = intent == "logistics"

    if not isinstance(action, str) or action not in VALID_ACTIONS:
        return _safe_fallback("action không hợp lệ", logistics=is_logistics)
    if (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not 0 <= confidence <= 1
    ):
        return _safe_fallback("confidence phải nằm trong khoảng 0–1", logistics=is_logistics)
    if not isinstance(reply, str) or not reply.strip():
        return _safe_fallback("reply phải là chuỗi không rỗng", logistics=is_logistics)
    if not isinstance(rationale, str) or not rationale.strip():
        return _safe_fallback(
            "rationale phải là chuỗi không rỗng", logistics=is_logistics
        )

    if confidence < LOW_CONFIDENCE_THRESHOLD and action not in LOW_CONFIDENCE_ACTIONS:
        return _safe_fallback(
            "confidence thấp nhưng action không hỏi lại hoặc handoff",
            logistics=is_logistics,
        )

    if is_logistics and not has_verified_logistics_source:
        if action != "handoff_to_ta":
            return _safe_fallback(
                "logistics không có nguồn phải chuyển TA", logistics=True
            )
        if _looks_like_ungrounded_logistics(reply):
            return _safe_fallback(
                "reply logistics chứa deadline, lịch hoặc link chưa có nguồn",
                logistics=True,
            )

    return cast(
        ModelOutput,
        {
            "intent": intent,
            "confidence": float(confidence),
            "action": action,
            "reply": reply.strip(),
            "rationale": rationale.strip(),
        },
    )

