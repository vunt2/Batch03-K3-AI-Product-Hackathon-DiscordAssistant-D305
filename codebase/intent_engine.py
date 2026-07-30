"""Rule-based mock intent engine for the CP2 clickable prototype.

CP2 only needs the main product flow to be demonstrable. This module keeps
classification deterministic and dependency-free so it can later be replaced
by a real model call in CP3 without changing the UI contract.
"""

from __future__ import annotations

import re
import unicodedata
from typing import TypedDict


class IntentResult(TypedDict):
    intent: str
    label: str
    confidence: float
    action: str
    action_label: str
    reply: str
    rationale: str


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


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return re.sub(r"\s+", " ", text).strip()


def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def classify_message(message: str) -> IntentResult:
    """Classify a learner message and return the prototype response decision."""

    normalized = _normalize(message)

    if not normalized:
        return _result(
            "ambiguous",
            0.99,
            "ask_clarifying_question",
            "Bạn muốn hỏi về bài học, deadline hay cách nộp bài? Hãy cho mình thêm một chút thông tin nhé.",
            "Tin nhắn chưa có nội dung để phân loại.",
        )

    out_of_scope_terms = (
        "lam ho",
        "viet ho",
        "dua dap an",
        "hack",
        "lay api key",
        "cho minh key",
        "thi ho",
    )
    logistics_terms = (
        "deadline",
        "han nop",
        "nop bai",
        "link nop",
        "lich hoc",
        "phong hoc",
        "zoom",
        "checkpoint",
        "cp2",
        "cp3",
        "demo luc",
    )
    learning_terms = (
        "khong hieu",
        "giai thich",
        "bai hoc",
        "prompt",
        "rag",
        "agent",
        "python",
        "api",
        "model",
        "intent",
        "classifier",
    )
    greeting_terms = (
        "xin chao",
        "chao",
        "hello",
        "hi",
        "cam on",
        "thank",
    )
    ambiguous_terms = (
        "cai nay",
        "lam sao",
        "giup minh",
        "giup em",
        "khong duoc",
        "bi loi",
    )

    if _contains_any(normalized, out_of_scope_terms):
        return _result(
            "out_of_scope",
            0.96,
            "decline_and_redirect",
            "Mình không thể làm bài hoặc cung cấp đáp án thay bạn. Mình có thể giải thích khái niệm, gợi ý từng bước hoặc xem phần bạn đã thử.",
            "Yêu cầu vượt quá phạm vi hỗ trợ học tập an toàn.",
        )

    if _contains_any(normalized, logistics_terms):
        return _result(
            "logistics",
            0.93,
            "handoff_to_ta",
            "Đây là thông tin có thể ảnh hưởng trực tiếp đến việc nộp bài. Bản CP2 chưa kết nối nguồn chính thức nên mình sẽ chuyển câu hỏi cho TA thay vì đoán.",
            "Phát hiện từ khóa logistics; chưa có nguồn chính thức để xác minh.",
        )

    if _contains_any(normalized, learning_terms):
        return _result(
            "learning",
            0.90,
            "answer_with_guidance",
            "Mình có thể giúp bạn học theo từng bước. Hãy gửi khái niệm hoặc đoạn bài bạn đang vướng và phần bạn đã thử; mình sẽ giải thích rồi đưa một ví dụ nhỏ.",
            "Tin nhắn chứa khái niệm hoặc tín hiệu hỏi nội dung học.",
        )

    if _contains_any(normalized, greeting_terms) and len(normalized.split()) <= 8:
        return _result(
            "greeting",
            0.95,
            "answer_briefly",
            "Chào bạn 👋 Mình có thể hỗ trợ câu hỏi bài học, logistics khóa học hoặc chuyển TA khi chưa chắc chắn.",
            "Tin nhắn ngắn mang tính chào hỏi hoặc cảm ơn.",
        )

    if _contains_any(normalized, ambiguous_terms) or len(normalized.split()) < 4:
        return _result(
            "ambiguous",
            0.72,
            "ask_clarifying_question",
            "Mình chưa đủ thông tin để trả lời chính xác. Bạn đang vướng ở bài nào, bước nào và đã thử điều gì rồi?",
            "Nội dung quá ngắn hoặc thiếu đối tượng cụ thể.",
        )

    return _result(
        "ambiguous",
        0.55,
        "ask_clarifying_question",
        "Mình chưa xác định chắc đây là câu hỏi bài học hay logistics. Bạn có thể nói rõ tên bài/chủ đề hoặc mốc cần hỏi không?",
        "Không có tín hiệu đủ mạnh để tự động trả lời.",
    )


def _result(
    intent: str,
    confidence: float,
    action: str,
    reply: str,
    rationale: str,
) -> IntentResult:
    return {
        "intent": intent,
        "label": INTENT_LABELS[intent],
        "confidence": confidence,
        "action": action,
        "action_label": ACTION_LABELS[action],
        "reply": reply,
        "rationale": rationale,
    }
