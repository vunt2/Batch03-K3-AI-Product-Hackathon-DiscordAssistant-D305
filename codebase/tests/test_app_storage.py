import unittest
from unittest.mock import patch

import _bootstrap  # noqa: F401

import app
from handoff_store import StoreError


class FakeSessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as error:
            raise AttributeError(name) from error

    def __setattr__(self, name, value):
        self[name] = value


class AppStorageFailureTest(unittest.TestCase):
    def test_initialize_state_handles_store_error(self):
        state = FakeSessionState()
        with patch.object(
            app,
            "initialize_store",
            side_effect=StoreError("Không thể kết nối kho handoff."),
        ), patch.object(app.st, "session_state", state):
            app.initialize_state()
            self.assertIs(state["storage_available"], False)
            self.assertTrue(len(state["storage_error_message"]) > 0)
            self.assertIn("learner_session_id", state)
            self.assertIn("messages", state)

    def test_reset_demo_session_handles_store_error(self):
        state = FakeSessionState(
            learner_session_id="session-test",
            messages=[{"role": "user", "content": "Câu hỏi thử"}],
            flash_message="",
            reset_confirmed=True,
            reset_notice=False,
            reset_error="",
        )
        with patch.object(
            app,
            "delete_session_handoffs",
            side_effect=StoreError("Lỗi kho dữ liệu."),
        ), patch.object(app.st, "session_state", state):
            app.reset_demo_session()
            self.assertEqual(len(state["messages"]), 1)
            self.assertEqual(state["messages"][0]["content"], "Câu hỏi thử")
            self.assertIs(state["reset_confirmed"], False)
            self.assertIs(state["reset_notice"], False)
            self.assertTrue(len(state["reset_error"]) > 0)


if __name__ == "__main__":
    unittest.main()
