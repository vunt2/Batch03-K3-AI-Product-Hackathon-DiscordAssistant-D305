"""CP3 Real LLM Intent Classification Engine with Safety Contract Integration.

Replaces the CP2 rule-based mock engine with real model calls via model_client.py,
prompts.py, and output_contract.py while maintaining strict fallback policies.
"""

from __future__ import annotations

import os
import uuid
from typing import TypedDict

from dotenv import load_dotenv

from model_client import (
    ModelClientError,
    ModelKeyMissingError,
    ModelResponseError,
    ModelTimeoutError,
    call_model_api,
    get_model_config,
)
from output_contract import validate_model_output
from prompts import build_system_prompt

# Load environment variables from .env if present
load_dotenv()


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


INTENT_LABELS = {
    "greeting": "Chào hỏi",
    "learning": "Hỏi bài",
    "logistics": "Logistics",
    "ambiguous": "Thiếu thông tin",
    "out_of_scope": "Ngoài phạm vi",
}

ACTION_LABELS = {
    "answer_briefly": "Trả lời ngắn",
    "answer_with_guidance": "Hướng dẫn học",
    "ask_clarifying_question": "Hỏi lại",
    "handoff_to_ta": "Chuyển TA",
    "decline_and_redirect": "Từ chối + định hướng",
}


def classify_message(
    message: str,
    verified_context: str | None = None,
    use_mock: bool = False,
) -> IntentResult:
    """Classify a learner message using real LLM API with safety contract validation."""
    trace_id = f"trace-{uuid.uuid4().hex[:8]}"
    clean_message = message.strip()

    if not clean_message:
        return _result(
            intent="ambiguous",
            confidence=1.0,
            action="ask_clarifying_question",
            reply="Bạn muốn hỏi về bài học, deadline hay cách nộp bài? Hãy cho mình thêm một chút thông tin nhé.",
            rationale="Tin nhắn chưa có nội dung để phân loại.",
            is_fallback=True,
            model_name="Validation Rule",
            trace_id=trace_id,
        )

    api_key, model_name = get_model_config()

    # Fallback if API key is missing or mock mode requested
    if use_mock or not api_key:
        return _handle_missing_key_fallback(clean_message, model_name or "Mock Engine", trace_id)

    # Build prompt with verified context
    system_prompt = build_system_prompt(verified_context)

    try:
        raw_output = call_model_api(system_prompt, clean_message)
        validated = validate_model_output(
            raw_output,
            has_verified_logistics_source=bool(verified_context),
        )

        is_fallback_used = "Fallback" in validated.get("rationale", "")
        return _result(
            intent=validated["intent"],
            confidence=validated["confidence"],
            action=validated["action"],
            reply=validated["reply"],
            rationale=validated["rationale"],
            is_fallback=is_fallback_used,
            model_name=model_name,
            trace_id=trace_id,
        )

    except ModelKeyMissingError:
        return _handle_missing_key_fallback(clean_message, model_name, trace_id)
    except ModelTimeoutError as err:
        return _result(
            intent="ambiguous",
            confidence=0.0,
            action="ask_clarifying_question",
            reply="Hệ thống phản hồi quá thời gian cho phép. Bạn có thể thử lại hoặc gửi thông tin cụ thể hơn.",
            rationale=f"Model Timeout: {err}",
            is_fallback=True,
            model_name=model_name,
            trace_id=trace_id,
        )
    except (ModelResponseError, ModelClientError, Exception) as err:
        return _result(
            intent="ambiguous",
            confidence=0.0,
            action="ask_clarifying_question",
            reply="Trợ lý đang gặp sự cố kết nối với AI. Bạn có thể gửi lại câu hỏi hoặc yêu cầu TA hỗ trợ.",
            rationale=f"API/Network Error: {err}",
            is_fallback=True,
            model_name=model_name,
            trace_id=trace_id,
        )


def _handle_missing_key_fallback(
    message: str,
    model_name: str,
    trace_id: str,
) -> IntentResult:
    """Return graceful fallback when MODEL_API_KEY is not configured."""
    return _result(
        intent="ambiguous",
        confidence=0.0,
        action="ask_clarifying_question",
        reply=(
            "Chưa cấu hình MODEL_API_KEY cho trợ lý AI. "
            "Vui lòng thêm API Key vào file .env để kích hoạt AI thật. "
            "Hiện tại hệ thống đang ở chế độ Safety Fallback."
        ),
        rationale="Cảnh báo: Thiếu MODEL_API_KEY trong môi trường.",
        is_fallback=True,
        model_name=f"{model_name} (Missing Key)",
        trace_id=trace_id,
    )


def _result(
    intent: str,
    confidence: float,
    action: str,
    reply: str,
    rationale: str,
    is_fallback: bool,
    model_name: str,
    trace_id: str,
) -> IntentResult:
    return {
        "intent": intent,
        "label": INTENT_LABELS.get(intent, intent),
        "confidence": confidence,
        "action": action,
        "action_label": ACTION_LABELS.get(action, action),
        "reply": reply,
        "rationale": rationale,
        "is_fallback": is_fallback,
        "model_name": model_name,
        "trace_id": trace_id,
    }
