import unittest
import _bootstrap  # noqa: F401

from conversation_context import (
    MAX_CURRENT_MESSAGE_CHARS,
    MAX_HISTORY_MESSAGES,
    MAX_MESSAGE_CHARS,
    MAX_TOTAL_CHARS,
    prepare_conversation_history,
    prepare_current_message,
)


class ConversationContextTest(unittest.TestCase):
    def test_empty_or_none_returns_empty_list(self):
        self.assertEqual(prepare_conversation_history(None), [])
        self.assertEqual(prepare_conversation_history([]), [])

    def test_ignores_welcome_message_and_invalid_schema(self):
        raw = [
            {
                "role": "assistant",
                "content": "Chào bạn! Mình có thể tìm câu trả lời từ nguồn...",
            },
            "invalid string item",
            {"role": "user", "content": ""},
            {"invalid_key": "val"},
            {"role": "user", "content": "Session state trong Streamlit?"},
        ]
        history = prepare_conversation_history(raw)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(
            history[0]["content"], "Session state trong Streamlit?"
        )

    def test_strips_internal_metadata_and_does_not_mutate_input(self):
        input_msg = [
            {
                "role": "user",
                "content": "Hỏi bài Streamlit",
                "trace_id": "trace-123",
                "result": {"intent": "learning"},
            },
            {
                "role": "assistant",
                "content": "Đây là câu trả lời",
                "knowledge_id": "KB-001",
            },
        ]
        history = prepare_conversation_history(input_msg)
        self.assertEqual(
            history,
            [
                {"role": "user", "content": "Hỏi bài Streamlit"},
                {"role": "assistant", "content": "Đây là câu trả lời"},
            ],
        )
        self.assertIn("trace_id", input_msg[0])

    def test_limits_max_messages_to_six(self):
        raw = []
        for i in range(10):
            role = "user" if i % 2 == 0 else "assistant"
            raw.append({"role": role, "content": f"Msg {i}"})
        history = prepare_conversation_history(raw)
        self.assertLessEqual(len(history), MAX_HISTORY_MESSAGES)
        self.assertEqual(history[0]["role"], "user")

    def test_truncates_long_messages_and_budget(self):
        long_content = "A" * (MAX_MESSAGE_CHARS + 500)
        raw = [{"role": "user", "content": long_content}]
        history = prepare_conversation_history(raw)
        self.assertEqual(len(history[0]["content"]), MAX_MESSAGE_CHARS)

    def test_redacts_secrets_in_history(self):
        secret_key = "AIza" + "B" * 24
        raw = [{"role": "user", "content": f"Key của tôi là {secret_key}"}]
        history = prepare_conversation_history(raw)
        self.assertNotIn(secret_key, history[0]["content"])
        self.assertIn("[REDACTED]", history[0]["content"])

    def test_ensures_alternating_roles_starting_with_user(self):
        raw = [
            {"role": "assistant", "content": "Ignore this first assistant"},
            {"role": "user", "content": "First user msg"},
            {"role": "user", "content": "Second user msg"},
            {"role": "assistant", "content": "Assistant msg"},
        ]
        history = prepare_conversation_history(raw)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Second user msg")
        self.assertEqual(history[1]["role"], "assistant")

    def test_excludes_labcoach_response_field(self):
        unapproved_text = "SECRET_UNAPPROVED_LABCOACH_RESPONSE_12345"
        raw = [
            {"role": "user", "content": "Hỏi câu hỏi 1"},
            {
                "role": "assistant",
                "content": "Nội dung bot trả lời",
                "labcoach_response": unapproved_text,
            },
        ]
        history = prepare_conversation_history(raw)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[1]["content"], "Nội dung bot trả lời")
        self.assertNotIn("labcoach_response", history[1])
        self.assertNotIn(unapproved_text, str(history))

    def test_total_character_budget_4000(self):
        raw = []
        for i in range(6):
            role = "user" if i % 2 == 0 else "assistant"
            raw.append({"role": role, "content": "X" * 800})
        history = prepare_conversation_history(raw)
        total_len = sum(len(turn["content"]) for turn in history)
        self.assertLessEqual(total_len, MAX_TOTAL_CHARS)

    def test_prepare_current_message_redacts_and_truncates(self):
        secret_key = "AIza" + "C" * 24
        long_input = f"Key: {secret_key} " + "Z" * 5000
        safe = prepare_current_message(long_input)
        self.assertNotIn(secret_key, safe)
        self.assertIn("[REDACTED]", safe)
        self.assertLessEqual(len(safe), MAX_CURRENT_MESSAGE_CHARS)
        # Verify original input string is not mutated
        self.assertIn(secret_key, long_input)


if __name__ == "__main__":
    unittest.main()
