"""Gemini intent routing with approved-source metadata and safe fallbacks."""

from __future__ import annotations

import re
import uuid
from typing import TypedDict

from conversation_context import (
    extract_preferred_name,
    prepare_conversation_history,
    prepare_current_message,
)
from knowledge_base import (
    KnowledgeMatch,
    knowledge_match_to_context,
    retrieve_approved_match,
)
from model_client import (
    ModelClientError,
    ModelKeyMissingError,
    ModelRateLimitError,
    ModelTimeoutError,
    call_gemini_api,
    get_gemini_config,
)
from output_contract import validate_model_output
from prompts import build_system_prompt


class IntentResult(TypedDict):
    intent: str
    label: str
    confidence: float
    action: str
    action_label: str
    reply: str
    rationale: str
    is_fallback: bool
    model_name: str
    trace_id: str
    model_requested: str
    model_used: str
    used_fallback: bool
    error_type: str
    error_code: int | None
    knowledge_id: str | None
    source_ids: list[str]
    topic: str | None
    source_verified: bool


INTENT_LABELS = {
    "greeting": "Chào hỏi",
    "learning": "Hỏi bài",
    "logistics": "Thông tin khóa học",
    "ambiguous": "Cần làm rõ",
    "out_of_scope": "Ngoài phạm vi",
}

ACTION_LABELS = {
    "answer_briefly": "Trả lời",
    "ask_clarifying_question": "Hỏi lại",
    "handoff_to_ta": "Chuyển Labcoach",
    "refuse_and_redirect": "Từ chối và định hướng",
}

LOGISTICS_PATTERN = re.compile(
    r"\b(deadline|hạn|lịch|mấy giờ|khi nào|nộp|submit|weekly|daily|"
    r"mentor duty|team|zoom|discord|github|xp|showcase|ticket)\b",
    re.IGNORECASE,
)
HOMEWORK_PATTERN = re.compile(
    r"\b(làm hộ|làm giúp toàn bộ|đáp án hoàn chỉnh|giải hộ|viết hộ|"
    r"chép đáp án|do my homework)\b",
    re.IGNORECASE,
)
CASUAL_PATTERN = re.compile(
    r"\b(?:xin chào|chào|hello|hi|hú lô|bot ơi|cảm ơn|thank|adu|slay|"
    r"căng vậy|xin vía|hay thế)\b",
    re.IGNORECASE,
)


def classify_message(
    message: str,
    *,
    conversation_history: list[dict[str, str]] | None = None,
    preferred_name: str | None = None,
    use_mock: bool = False,
) -> IntentResult:
    """Route one learner message and return UI-safe structured metadata."""

    trace_id = f"trace-{uuid.uuid4().hex[:8]}"
    clean_message = message.strip()
    config = get_gemini_config()
    metadata = config.public_metadata()
    knowledge_match = (
        retrieve_approved_match(clean_message) if clean_message else None
    )

    if not clean_message:
        return _result(
            intent="ambiguous",
            confidence=1.0,
            action="ask_clarifying_question",
            reply="Bạn muốn hỏi về nội dung nào? Hãy cho mình thêm một chút thông tin nhé.",
            rationale="Tin nhắn chưa có nội dung để phân loại.",
            is_fallback=True,
            trace_id=trace_id,
            metadata=metadata,
            knowledge_match=None,
        )

    if use_mock or not config.is_configured:
        return _safe_local_fallback(
            clean_message,
            trace_id,
            metadata,
            knowledge_match,
            error_type="missing_api_key" if not config.is_configured else "",
        )

    safe_history = (
        prepare_conversation_history(conversation_history)
        if conversation_history
        else None
    )
    safe_model_message = prepare_current_message(clean_message)
    verified_context = knowledge_match_to_context(knowledge_match)
    try:
        raw_output = call_gemini_api(
            build_system_prompt(
                verified_context,
                preferred_name=preferred_name,
            ),
            safe_model_message,
            conversation_history=safe_history,
            config=config,
            metadata_out=metadata,
        )
        validated = validate_model_output(
            raw_output,
            has_verified_logistics_source=bool(knowledge_match),
        )
        is_contract_fallback = validated["rationale"].startswith(
            "Fallback an toàn:"
        )
        if is_contract_fallback:
            metadata["used_fallback"] = True

        if (
            not is_contract_fallback
            and not knowledge_match
            and _is_casual_message(clean_message)
            and (
                validated["intent"] != "greeting"
                or validated["action"] != "answer_briefly"
            )
        ):
            metadata["used_fallback"] = True
            return _result(
                intent="greeting",
                confidence=1.0,
                action="answer_briefly",
                reply=_casual_fallback_reply(clean_message),
                rationale=(
                    "Casual chat vô hại được định tuyến lại để không tạo handoff."
                ),
                is_fallback=True,
                trace_id=trace_id,
                metadata=metadata,
                knowledge_match=None,
            )

        reply = validated["reply"]
        if (
            knowledge_match
            and validated["intent"] == "logistics"
            and validated["action"] == "answer_briefly"
        ):
            # Logistics displayed to learners must be exact approved knowledge,
            # never a model-authored paraphrase with extra claims.
            reply = knowledge_match["answer"]

        return _result(
            intent=validated["intent"],
            confidence=validated["confidence"],
            action=validated["action"],
            reply=reply,
            rationale=validated["rationale"],
            is_fallback=is_contract_fallback,
            trace_id=trace_id,
            metadata=metadata,
            knowledge_match=knowledge_match,
        )
    except ModelKeyMissingError:
        return _safe_local_fallback(
            clean_message,
            trace_id,
            metadata,
            knowledge_match,
            error_type="missing_api_key",
        )
    except ModelRateLimitError as error:
        return _safe_local_fallback(
            clean_message,
            trace_id,
            metadata,
            knowledge_match,
            error_type=error.error_type,
            error_code=error.status_code,
            friendly_reason="Gemini đang bận. Trợ lý đã chuyển sang chế độ an toàn.",
        )
    except ModelTimeoutError as error:
        return _safe_local_fallback(
            clean_message,
            trace_id,
            metadata,
            knowledge_match,
            error_type=error.error_type,
            error_code=error.status_code,
            friendly_reason="Gemini phản hồi chậm. Trợ lý đã chuyển sang chế độ an toàn.",
        )
    except ModelClientError as error:
        return _safe_local_fallback(
            clean_message,
            trace_id,
            metadata,
            knowledge_match,
            error_type=error.error_type,
            error_code=error.status_code,
            friendly_reason="Gemini tạm thời chưa sẵn sàng. Trợ lý đã chuyển sang chế độ an toàn.",
        )
    except Exception:
        return _safe_local_fallback(
            clean_message,
            trace_id,
            metadata,
            knowledge_match,
            error_type="unexpected_error",
            friendly_reason="Trợ lý gặp sự cố tạm thời và đã chuyển sang chế độ an toàn.",
        )


def _safe_local_fallback(
    message: str,
    trace_id: str,
    metadata: dict[str, object],
    knowledge_match: KnowledgeMatch | None,
    *,
    error_type: str = "",
    error_code: int | None = None,
    friendly_reason: str = "Gemini chưa được cấu hình. Trợ lý đang dùng chế độ an toàn.",
) -> IntentResult:
    metadata["used_fallback"] = True

    if knowledge_match:
        return _result(
            intent="logistics",
            confidence=1.0,
            action="answer_briefly",
            reply=knowledge_match["answer"],
            rationale=(
                f"{friendly_reason} Câu trả lời được lấy nguyên văn từ nguồn đã xác minh."
            ),
            is_fallback=True,
            trace_id=trace_id,
            metadata=metadata,
            knowledge_match=knowledge_match,
            error_type=error_type,
            error_code=error_code,
        )
    if HOMEWORK_PATTERN.search(message):
        return _result(
            intent="out_of_scope",
            confidence=1.0,
            action="refuse_and_redirect",
            reply=(
                "Mình không thể làm hộ hoặc cung cấp đáp án hoàn chỉnh. "
                "Bạn hãy gửi phần đã làm và chỗ đang vướng, mình sẽ gợi ý từng bước."
            ),
            rationale=f"{friendly_reason} Yêu cầu làm hộ được từ chối an toàn.",
            is_fallback=True,
            trace_id=trace_id,
            metadata=metadata,
            knowledge_match=None,
            error_type=error_type,
            error_code=error_code,
        )
    if _is_casual_message(message):
        return _result(
            intent="greeting",
            confidence=1.0,
            action="answer_briefly",
            reply=_casual_fallback_reply(message),
            rationale=f"{friendly_reason} Casual chat vô hại được trả lời ngắn gọn.",
            is_fallback=True,
            trace_id=trace_id,
            metadata=metadata,
            knowledge_match=None,
            error_type=error_type,
            error_code=error_code,
        )
    if LOGISTICS_PATTERN.search(message):
        return _result(
            intent="logistics",
            confidence=1.0,
            action="handoff_to_ta",
            reply=(
                "Mình chưa có nguồn đã xác minh phù hợp với câu hỏi này. "
                "Mình đã chuyển câu hỏi cho Labcoach hỗ trợ."
            ),
            rationale=f"{friendly_reason} Logistics không có nguồn phù hợp phải handoff.",
            is_fallback=True,
            trace_id=trace_id,
            metadata=metadata,
            knowledge_match=None,
            error_type=error_type,
            error_code=error_code,
        )
    return _result(
        intent="ambiguous",
        confidence=0.0,
        action="ask_clarifying_question",
        reply=(
            "Mình chưa thể xử lý câu hỏi này ngay lúc này. "
            "Bạn có thể mô tả rõ nội dung và điều bạn đang vướng không?"
        ),
        rationale=f"{friendly_reason} Không đủ căn cứ để trả lời.",
        is_fallback=True,
        trace_id=trace_id,
        metadata=metadata,
        knowledge_match=None,
        error_type=error_type,
        error_code=error_code,
    )


def _is_casual_message(message: str) -> bool:
    """Return True only for short harmless casual messages without course asks."""

    clean = message.strip()
    if not clean or len(clean) > 160:
        return False
    if HOMEWORK_PATTERN.search(clean) or LOGISTICS_PATTERN.search(clean):
        return False
    if extract_preferred_name(clean):
        return True
    return bool(CASUAL_PATTERN.search(clean))


def _casual_fallback_reply(message: str) -> str:
    """Provide varied, brief local replies without inventing course facts."""

    lowered = message.casefold()
    if "cảm ơn" in lowered or "thank" in lowered:
        return "Không có gì nha! Cần gì cứ gọi mình nhé 🙂"
    if "xin vía" in lowered:
        return "Gửi bạn chút vía tự tin nè ✨ Cứ bám checklist và làm từng bước nhé!"
    if any(term in lowered for term in ("slay", "adu", "căng vậy", "hay thế")):
        return "Haha, năng lượng lên cao rồi đó 😄 Mình vẫn ở đây nếu bạn cần hỗ trợ!"
    return "Hú lô! Mình đây 👋 Bạn muốn hỏi gì nào?"


def _result(
    *,
    intent: str,
    confidence: float,
    action: str,
    reply: str,
    rationale: str,
    is_fallback: bool,
    trace_id: str,
    metadata: dict[str, object],
    knowledge_match: KnowledgeMatch | None,
    error_type: str = "",
    error_code: int | None = None,
) -> IntentResult:
    model_used = str(metadata.get("model_used", "gemini"))
    return {
        "intent": intent,
        "label": INTENT_LABELS.get(intent, intent),
        "confidence": confidence,
        "action": action,
        "action_label": ACTION_LABELS.get(action, action),
        "reply": reply,
        "rationale": rationale,
        "is_fallback": is_fallback,
        "model_name": model_used,
        "trace_id": trace_id,
        "model_requested": str(metadata.get("model_requested", "gemini")),
        "model_used": model_used,
        "used_fallback": bool(metadata.get("used_fallback", is_fallback)),
        "error_type": error_type,
        "error_code": error_code,
        "knowledge_id": (
            knowledge_match["knowledge_id"] if knowledge_match else None
        ),
        "source_ids": (
            list(knowledge_match["source_ids"]) if knowledge_match else []
        ),
        "topic": knowledge_match["topic"] if knowledge_match else None,
        "source_verified": bool(
            knowledge_match and knowledge_match["source_verified"]
        ),
    }
