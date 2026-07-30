import json
import os
import unittest
from unittest.mock import patch

import _bootstrap  # noqa: F401

from intent_engine import classify_message
from model_client import ModelTimeoutError


GEMINI_ENV = {
    "GEMINI_API_KEY": "unit-test-gemini-key",
    "GEMINI_MODEL": "gemini-3.5-flash-lite",
    "GEMINI_TIMEOUT_SECONDS": "30",
}


def model_output(**overrides):
    payload = {
        "intent": "greeting",
        "confidence": 0.95,
        "action": "answer_briefly",
        "reply": "Xin chào.",
        "rationale": "Chào hỏi.",
    }
    payload.update(overrides)
    return json.dumps(payload, ensure_ascii=False)


APPROVED_MATCH = {
    "knowledge_id": "KB-006",
    "source_ids": ["IMG-010", "IMG-013", "IMG-029"],
    "topic": "submission",
    "source_verified": True,
    "answer": (
        "Dùng /weekly submit; form yêu cầu tiến độ, blockers, kế hoạch và "
        "link đính kèm; không cần Word/PDF riêng."
    ),
}


class IntentEngineTest(unittest.TestCase):
    def test_missing_key_does_not_call_network_and_handoffs_logistics(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch(
                "intent_engine.retrieve_approved_match",
                return_value=None,
            ):
                with patch("intent_engine.call_gemini_api") as call:
                    result = classify_message("Deadline mới là khi nào?")
        call.assert_not_called()
        self.assertEqual(result["intent"], "logistics")
        self.assertEqual(result["action"], "handoff_to_ta")
        self.assertTrue(result["used_fallback"])
        self.assertFalse(result["source_verified"])

    def test_logistics_with_source_returns_exact_approved_answer(self):
        raw = model_output(
            intent="logistics",
            action="answer_briefly",
            reply="Một câu diễn giải có thể thêm thông tin.",
            rationale="Có nguồn phù hợp.",
        )
        with patch.dict(os.environ, GEMINI_ENV, clear=True):
            with patch(
                "intent_engine.retrieve_approved_match",
                return_value=APPROVED_MATCH,
            ):
                with patch(
                    "intent_engine.call_gemini_api",
                    return_value=raw,
                ):
                    result = classify_message(
                        "Weekly report cần nộp nội dung gì?"
                    )
        self.assertEqual(result["action"], "answer_briefly")
        self.assertEqual(result["reply"], APPROVED_MATCH["answer"])
        self.assertEqual(result["knowledge_id"], "KB-006")
        self.assertTrue(result["source_verified"])

    def test_logistics_without_source_discards_model_claim(self):
        raw = model_output(
            intent="logistics",
            action="answer_briefly",
            reply="Deadline là ngày 20/08.",
            rationale="Đoán deadline.",
        )
        with patch.dict(os.environ, GEMINI_ENV, clear=True):
            with patch(
                "intent_engine.retrieve_approved_match",
                return_value=None,
            ):
                with patch(
                    "intent_engine.call_gemini_api",
                    return_value=raw,
                ):
                    result = classify_message("Deadline mới là khi nào?")
        self.assertEqual(result["action"], "handoff_to_ta")
        self.assertNotIn("20/08", result["reply"])
        self.assertEqual(result["source_ids"], [])

    def test_valid_ungrounded_handoff_is_not_contract_fallback(self):
        raw = model_output(
            intent="logistics",
            action="handoff_to_ta",
            reply="Mình sẽ chuyển Labcoach xác nhận.",
            rationale="Không có nguồn approved phù hợp.",
        )
        with patch.dict(os.environ, GEMINI_ENV, clear=True):
            with patch(
                "intent_engine.retrieve_approved_match",
                return_value=None,
            ):
                with patch(
                    "intent_engine.call_gemini_api",
                    return_value=raw,
                ):
                    result = classify_message("Nhà ăn mấy giờ đóng cửa?")
        self.assertEqual(result["action"], "handoff_to_ta")
        self.assertFalse(result["used_fallback"])
        self.assertEqual(result["source_ids"], [])

    def test_malformed_json_returns_contract_fallback(self):
        with patch.dict(os.environ, GEMINI_ENV, clear=True):
            with patch(
                "intent_engine.retrieve_approved_match",
                return_value=None,
            ):
                with patch(
                    "intent_engine.call_gemini_api",
                    return_value="not-json",
                ):
                    result = classify_message("Xin chào")
        self.assertEqual(result["action"], "ask_clarifying_question")
        self.assertTrue(result["used_fallback"])

    def test_timeout_returns_safe_fallback(self):
        with patch.dict(os.environ, GEMINI_ENV, clear=True):
            with patch(
                "intent_engine.retrieve_approved_match",
                return_value=None,
            ):
                with patch(
                    "intent_engine.call_gemini_api",
                    side_effect=ModelTimeoutError(
                        "timeout",
                        error_type="timeout",
                    ),
                ):
                    result = classify_message("Nhà ăn mấy giờ đóng cửa?")
        self.assertEqual(result["action"], "handoff_to_ta")
        self.assertTrue(result["used_fallback"])

    def test_homework_request_is_refused_without_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch(
                "intent_engine.retrieve_approved_match",
                return_value=None,
            ):
                result = classify_message(
                    "Làm hộ mình toàn bộ bài và đưa đáp án hoàn chỉnh."
                )
        self.assertEqual(result["intent"], "out_of_scope")
        self.assertEqual(result["action"], "refuse_and_redirect")

    def test_secret_from_model_is_redacted(self):
        secret = "AIza" + "A" * 24
        raw = model_output(reply=f"Không chia sẻ {secret}.")
        with patch.dict(os.environ, GEMINI_ENV, clear=True):
            with patch(
                "intent_engine.retrieve_approved_match",
                return_value=None,
            ):
                with patch(
                    "intent_engine.call_gemini_api",
                    return_value=raw,
                ):
                    result = classify_message("Xin chào")
        self.assertNotIn(secret, repr(result))
        self.assertIn("[REDACTED]", result["reply"])


if __name__ == "__main__":
    unittest.main()
