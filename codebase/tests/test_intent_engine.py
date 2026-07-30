import json
import unittest
from unittest.mock import patch

from intent_engine import classify_message
from model_client import ModelTimeoutError


class IntentEngineTest(unittest.TestCase):
    def test_missing_api_key_returns_safe_fallback(self):
        with patch("intent_engine.get_model_config", return_value=("", "gemini-1.5-flash")):
            result = classify_message("Xin chào bot")
            self.assertTrue(result["is_fallback"])
            self.assertEqual(result["intent"], "ambiguous")
            self.assertEqual(result["action"], "ask_clarifying_question")

    def test_valid_llm_call_greeting(self):
        mock_response = json.dumps({
            "intent": "greeting",
            "confidence": 0.95,
            "action": "answer_briefly",
            "reply": "Chào bạn 👋 Trợ lý học tập sẵn sàng hỗ trợ!",
            "rationale": "Tin nhắn chào hỏi ngắn."
        })
        with patch("intent_engine.get_model_config", return_value=("fake-key", "gemini-1.5-flash")):
            with patch("intent_engine.call_model_api", return_value=mock_response):
                result = classify_message("Xin chào bot")
                self.assertFalse(result["is_fallback"])
                self.assertEqual(result["intent"], "greeting")
                self.assertEqual(result["action"], "answer_briefly")
                self.assertEqual(result["label"], "Chào hỏi")

    def test_learning_question(self):
        mock_response = json.dumps({
            "intent": "learning",
            "confidence": 0.92,
            "action": "answer_with_guidance",
            "reply": "RAG (Retrieval-Augmented Generation) là kĩ thuật...",
            "rationale": "Hỏi khái niệm RAG"
        })
        with patch("intent_engine.get_model_config", return_value=("fake-key", "gemini-1.5-flash")):
            with patch("intent_engine.call_model_api", return_value=mock_response):
                result = classify_message("Giải thích giúp mình RAG là gì")
                self.assertEqual(result["intent"], "learning")
                self.assertEqual(result["action"], "answer_with_guidance")

    def test_logistics_without_context_discards_model_reply(self):
        mock_response = json.dumps({
            "intent": "logistics",
            "confidence": 0.99,
            "action": "answer_briefly",
            "reply": "Deadline CP2 là 23:59 hôm nay.",
            "rationale": "Hỏi deadline nộp CP2"
        })
        with patch("intent_engine.get_model_config", return_value=("fake-key", "gemini-1.5-flash")):
            with patch("intent_engine.call_model_api", return_value=mock_response):
                result = classify_message("Deadline nộp CP2 là khi nào?")
                self.assertEqual(result["intent"], "logistics")
                self.assertEqual(result["action"], "handoff_to_ta")
                self.assertNotIn("23:59", result["reply"])
                self.assertTrue(result["is_fallback"])

    def test_timeout_error_returns_fallback(self):
        with patch("intent_engine.get_model_config", return_value=("fake-key", "gemini-1.5-flash")):
            with patch("intent_engine.call_model_api", side_effect=ModelTimeoutError("Timeout")):
                result = classify_message("Cái này làm sao?")
                self.assertTrue(result["is_fallback"])
                self.assertEqual(result["intent"], "ambiguous")
                self.assertEqual(result["action"], "ask_clarifying_question")

    def test_out_of_scope_request_is_declined(self):
        mock_response = json.dumps({
            "intent": "out_of_scope",
            "confidence": 0.98,
            "action": "decline_and_redirect",
            "reply": "Mình không thể làm bài giúp bạn. Mình có thể gợi ý từng bước...",
            "rationale": "Yêu cầu làm bài hộ."
        })
        with patch("intent_engine.get_model_config", return_value=("fake-key", "gemini-1.5-flash")):
            with patch("intent_engine.call_model_api", return_value=mock_response):
                result = classify_message("Làm hộ mình toàn bộ bài này")
                self.assertEqual(result["intent"], "out_of_scope")
                self.assertEqual(result["action"], "decline_and_redirect")


if __name__ == "__main__":
    unittest.main()
