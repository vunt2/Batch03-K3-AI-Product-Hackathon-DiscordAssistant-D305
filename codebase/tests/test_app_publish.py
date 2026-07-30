import unittest
from unittest.mock import MagicMock, patch

import _bootstrap  # noqa: F401

import app
from knowledge_publisher import KnowledgePublishError


class AppPublishTest(unittest.TestCase):
    @patch("app.publish_candidate")
    def test_execute_candidate_publish_success(self, mock_publish):
        mock_publish.return_value = {
            "id": "KB-LC-TEST1234",
            "topic": "submission",
            "canonical_question": "Nộp bài?",
            "answer": "Nộp qua LMS",
        }

        ok, msg = app.execute_candidate_publish(
            candidate_id="KC-TEST1234",
            topic="submission",
            volatile=False,
            valid_until=None,
        )

        self.assertTrue(ok)
        self.assertIn("KB-LC-TEST1234", msg)
        mock_publish.assert_called_once_with(
            candidate_id="KC-TEST1234",
            topic="submission",
            volatile=False,
            valid_until=None,
        )

    @patch("app.publish_candidate")
    def test_execute_candidate_publish_knowledge_publish_error(self, mock_publish):
        mock_publish.side_effect = KnowledgePublishError(
            "internal path=C:/secret/data.json api_key=AIzaSecret123"
        )

        ok, msg = app.execute_candidate_publish(
            candidate_id="KC-TEST5678",
            topic="schedule",
            volatile=True,
            valid_until="2026-12-31",
        )

        self.assertFalse(ok)
        self.assertEqual(
            msg,
            "Không thể publish knowledge. Vui lòng kiểm tra trạng thái "
            "candidate và thông tin đã nhập.",
        )
        self.assertNotIn("internal path", msg)
        self.assertNotIn("C:/secret/data.json", msg)
        self.assertNotIn("AIzaSecret123", msg)
        mock_publish.assert_called_once_with(
            candidate_id="KC-TEST5678",
            topic="schedule",
            volatile=True,
            valid_until="2026-12-31",
        )

    @patch("app.publish_candidate")
    def test_execute_candidate_publish_preserves_none_valid_until(self, mock_publish):
        mock_publish.return_value = {"id": "KB-LC-9999"}

        ok, msg = app.execute_candidate_publish(
            candidate_id="KC-9999",
            topic="logistics",
            volatile=False,
            valid_until=None,
        )

        self.assertTrue(ok)
        _, kwargs = mock_publish.call_args
        self.assertIsNone(kwargs["valid_until"])

    @patch("app.publish_candidate")
    @patch("app.st")
    def test_execute_candidate_publish_does_not_call_rerun(self, mock_st, mock_publish):
        mock_publish.return_value = {"id": "KB-LC-RERUN"}

        ok, msg = app.execute_candidate_publish(
            candidate_id="KC-RERUN",
            topic="topic",
            volatile=False,
            valid_until=None,
        )

        self.assertTrue(ok)
        mock_st.rerun.assert_not_called()

    @patch("app.publish_candidate")
    def test_execute_candidate_publish_does_not_catch_generic_exceptions(self, mock_publish):
        mock_publish.side_effect = RuntimeError("Unexpected internal crash")

        with self.assertRaises(RuntimeError) as cm:
            app.execute_candidate_publish(
                candidate_id="KC-CRASH",
                topic="topic",
                volatile=False,
                valid_until=None,
            )

        self.assertEqual(str(cm.exception), "Unexpected internal crash")


if __name__ == "__main__":
    unittest.main()
