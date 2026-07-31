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


def intent_result(
    *,
    intent="greeting",
    action="answer_briefly",
    reply="Chào bạn!",
):
    return {
        "intent": intent,
        "label": "Chào hỏi",
        "confidence": 0.95,
        "action": action,
        "action_label": "Trả lời",
        "reply": reply,
        "rationale": "Định tuyến thử nghiệm.",
        "is_fallback": False,
        "model_name": "gemini-3.5-flash-lite",
        "trace_id": "trace-test",
        "model_requested": "gemini-3.5-flash-lite",
        "model_used": "gemini-3.5-flash-lite",
        "used_fallback": False,
        "error_type": "",
        "error_code": None,
        "knowledge_id": None,
        "source_ids": [],
        "topic": None,
        "source_verified": False,
    }


def session_state(**overrides):
    state = FakeSessionState(
        messages=[dict(app.WELCOME_MESSAGE)],
        learner_display_name="",
        learner_session_id="session-test",
        storage_available=True,
        storage_error_message="",
        flash_message="",
        reset_confirmed=False,
        reset_notice=False,
        reset_error="",
    )
    state.update(overrides)
    return state


class AppConversationTest(unittest.TestCase):
    def test_initialize_state_creates_empty_session_name(self):
        state = FakeSessionState()
        with patch.object(app, "initialize_store"), patch.object(
            app.st,
            "session_state",
            state,
        ):
            app.initialize_state()
        self.assertEqual(state["learner_display_name"], "")

    def test_name_is_saved_and_passed_to_next_classifier_call(self):
        state = session_state()
        with patch.object(
            app.st,
            "session_state",
            state,
        ), patch.object(app.st, "spinner"), patch.object(
            app,
            "classify_message",
            return_value=intent_result(),
        ) as classify:
            app.submit_message("Mình tên là An")
            app.submit_message("Chào bot")

        self.assertEqual(state["learner_display_name"], "An")
        self.assertEqual(
            classify.call_args_list[1].kwargs["preferred_name"],
            "An",
        )

    def test_reset_session_clears_preferred_name(self):
        state = session_state(learner_display_name="An")
        with patch.object(
            app.st,
            "session_state",
            state,
        ), patch.object(app, "delete_session_handoffs"):
            app.reset_demo_session()

        self.assertEqual(state["learner_display_name"], "")

    def test_reset_error_still_clears_preferred_name(self):
        state = session_state(learner_display_name="An")
        with patch.object(
            app.st,
            "session_state",
            state,
        ), patch.object(
            app,
            "delete_session_handoffs",
            side_effect=StoreError("Lỗi kho dữ liệu."),
        ):
            app.reset_demo_session()

        self.assertEqual(state["learner_display_name"], "")

    def test_casual_chat_does_not_create_handoff(self):
        state = session_state()
        with patch.object(
            app.st,
            "session_state",
            state,
        ), patch.object(app.st, "spinner"), patch.object(
            app,
            "classify_message",
            return_value=intent_result(),
        ), patch.object(app, "create_handoff") as create_handoff:
            app.submit_message("adu nay căng vậy")

        create_handoff.assert_not_called()

    def test_name_is_not_written_to_handoff_store(self):
        state = session_state(learner_display_name="An")
        handoff_result = intent_result(
            intent="logistics",
            action="handoff_to_ta",
            reply="Mình sẽ chuyển Labcoach xác nhận.",
        )
        with patch.object(
            app.st,
            "session_state",
            state,
        ), patch.object(app.st, "spinner"), patch.object(
            app,
            "classify_message",
            return_value=handoff_result,
        ), patch.object(
            app,
            "create_handoff",
            return_value={"handoff_id": "handoff-test"},
        ) as create_handoff:
            app.submit_message("Deadline mới là khi nào?")

        stored_fields = create_handoff.call_args.kwargs
        self.assertNotIn("preferred_name", stored_fields)
        self.assertNotIn("learner_display_name", stored_fields)
        self.assertNotIn("An", repr(stored_fields))


if __name__ == "__main__":
    unittest.main()
