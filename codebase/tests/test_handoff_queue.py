import unittest

import _bootstrap  # noqa: F401

from handoff_queue import (
    PENDING,
    RESOLVED,
    enqueue_handoff,
    queue_counts,
    reopen_handoff,
    resolve_handoff,
)


class HandoffQueueTest(unittest.TestCase):
    def test_enqueue_deduplicates_pending_question(self):
        queue = []
        first = enqueue_handoff(
            queue,
            question="Deadline tạo team là khi nào?",
            intent="logistics",
            reason="Không có nguồn.",
            trace_id="trace-001",
            model="gemini-3.5-flash-lite",
        )
        second = enqueue_handoff(
            queue,
            question="  deadline tạo TEAM là khi nào? ",
            intent="logistics",
            reason="Không có nguồn.",
            trace_id="trace-002",
            model="gemini-3.5-flash-lite",
        )
        self.assertEqual(first, second)
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]["status"], PENDING)

    def test_resolve_and_reopen(self):
        queue = []
        handoff_id = enqueue_handoff(
            queue,
            question="Nhà ăn đóng cửa lúc mấy giờ?",
            intent="logistics",
            reason="Không có nguồn.",
            trace_id="trace-003",
            model="gemini-3.5-flash-lite",
        )
        self.assertTrue(
            resolve_handoff(queue, handoff_id, "Labcoach sẽ xác minh.")
        )
        self.assertEqual(queue[0]["status"], RESOLVED)
        self.assertEqual(
            queue[0]["labcoach_response"],
            "Labcoach sẽ xác minh.",
        )
        self.assertIsNotNone(queue[0]["resolved_at"])
        self.assertEqual(queue_counts(queue), (0, 1))

        self.assertTrue(reopen_handoff(queue, handoff_id))
        self.assertEqual(queue[0]["status"], PENDING)
        self.assertIsNone(queue[0]["resolved_at"])
        self.assertEqual(queue_counts(queue), (1, 0))

    def test_empty_response_does_not_resolve(self):
        queue = []
        handoff_id = enqueue_handoff(
            queue,
            question="Câu hỏi",
            intent="logistics",
            reason="Thiếu nguồn.",
            trace_id="trace-004",
            model="gemini-3.5-flash-lite",
        )
        self.assertFalse(resolve_handoff(queue, handoff_id, "  "))
        self.assertEqual(queue[0]["status"], PENDING)


if __name__ == "__main__":
    unittest.main()
