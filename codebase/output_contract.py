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
        "ask_clarifying_question",
        "handoff_to_ta",
        "refuse_and_redirect",
    }
)
EXPECTED_ACTIONS_BY_INTENT: Final[dict[str, frozenset[str]]] = {
    "greeting": frozenset({"answer_briefly"}),
    "learning": frozenset({"answer_briefly"}),
    "logistics": frozenset({"answer_briefly", "handoff_to_ta"}),
    "ambiguous": frozenset({"ask_clarifying_question"}),
    "out_of_scope": frozenset({"refuse_and_redirect"}),
}
REQUIRED_FIELDS: Final[frozenset[str]] = frozenset(
    {"intent", "confidence", "action", "reply", "rationale"}
)
LOW_CONFIDENCE_THRESHOLD: Final[float] = 0.70
LOW_CONFIDENCE_ACTIONS: Final[frozenset[str]] = frozenset(
    {"ask_clarifying_question", "handoff_to_ta"}
)
SAFE_LOGISTICS_REPLY: Final[str] = (
    "Mình chưa có nguồn chính thức để xác nhận thông tin này. "
    "Mình sẽ chuyển câu hỏi cho Labcoach hỗ trợ."
)

_GOOGLE_KEY_PATTERN = re.compile(r"\bAIza[A-Za-z0-9_-]{12,}\b")
_BEARER_TOKEN_PATTERN = re.compile(
    r"\bBearer\s+[A-Za-z0-9._~+/=-]{8,}",
    re.IGNORECASE,
)
_DISCORD_TOKEN_PATTERN = re.compile(
    r"\b[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{20,}\b"
)
_LABELLED_SECRET_PATTERN = re.compile(
    r"(?P<prefix>\b(?:password|secret|token|api[_ -]?key)\b\s*[:=]\s*)"
    r"(?P<quote>[\"']?)(?P<value>[^\s,;\"']{4,})(?P=quote)",
    re.IGNORECASE,
)
_LONG_TOKEN_PATTERN = re.compile(
    r"\b(?=[A-Za-z0-9_-]*[A-Za-z])(?=[A-Za-z0-9_-]*\d)"
    r"[A-Za-z0-9_-]{48,}\b"
)
_SELF_DESCRIBING_SECRET_PATTERN = re.compile(
    r"\b(?:secret|token|api_key|api-key|password)[_-]"
    r"(?=[A-Za-z0-9_-]*\d)[A-Za-z0-9_-]{8,}\b",
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
            "reply": SAFE_LOGISTICS_REPLY,
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


def redact_sensitive_text(text: str) -> str:
    """Replace common credentials and suspicious long tokens before display."""

    redacted = _LABELLED_SECRET_PATTERN.sub(
        lambda match: f"{match.group('prefix')}[REDACTED]", text
    )
    for pattern in (
        _GOOGLE_KEY_PATTERN,
        _BEARER_TOKEN_PATTERN,
        _DISCORD_TOKEN_PATTERN,
        _SELF_DESCRIBING_SECRET_PATTERN,
        _LONG_TOKEN_PATTERN,
    ):
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted
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

    if is_logistics and not has_verified_logistics_source:
        # Never retain model-authored logistics text without an approved source.
        if action == "handoff_to_ta":
            return {
                "intent": "logistics",
                "confidence": float(confidence),
                "action": "handoff_to_ta",
                "reply": SAFE_LOGISTICS_REPLY,
                "rationale": redact_sensitive_text(rationale.strip()),
            }
        return _safe_fallback(
            "logistics không có nguồn xác minh luôn dùng handoff cố định",
            logistics=True,
        )

    if confidence < LOW_CONFIDENCE_THRESHOLD:
        if action not in LOW_CONFIDENCE_ACTIONS:
            return _safe_fallback(
                "confidence thấp nhưng action không hỏi lại hoặc handoff",
                logistics=is_logistics,
            )
    elif action not in EXPECTED_ACTIONS_BY_INTENT[intent]:
        return _safe_fallback(
            "cặp intent/action không hợp lệ",
            logistics=is_logistics,
        )

    return cast(
        ModelOutput,
        {
            "intent": intent,
            "confidence": float(confidence),
            "action": action,
            "reply": redact_sensitive_text(reply.strip()),
            "rationale": redact_sensitive_text(rationale.strip()),
        },
    )

