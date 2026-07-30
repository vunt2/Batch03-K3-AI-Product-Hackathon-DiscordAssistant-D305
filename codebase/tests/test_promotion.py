import csv
from datetime import date
from pathlib import Path
import tempfile
import unittest

import _bootstrap  # noqa: F401

from knowledge_base import load_approved_knowledge, retrieve_approved_context
from promote_knowledge import (
    DEFAULT_CANDIDATES_PATH,
    DEFAULT_QUEUE_PATH,
    PromotionValidationError,
    promote_approved_knowledge,
)


def copy_queue_with_change(target: Path, candidate_id: str, field: str, value: str):
    with DEFAULT_QUEUE_PATH.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    for row in rows:
        if row["candidate_id"] == candidate_id:
            row[field] = value
    with target.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class PromotionTest(unittest.TestCase):
    def test_reviewed_queue_promotes_only_approved_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "course-knowledge.json"
            counts = promote_approved_knowledge(
                output_path=output,
            )
            entries = load_approved_knowledge(
                output,
                today=date(2026, 7, 30),
            )
            expired_context = retrieve_approved_context(
                "Thời hạn tạo team là khi nào?",
                output,
                today=date(2026, 7, 30),
            )
            unrelated_deadline = retrieve_approved_context(
                "Deadline nộp CP2 là khi nào?",
                output,
                today=date(2026, 7, 30),
            )
        self.assertEqual(
            counts,
            {"approved": 27, "expired": 2, "handoff": 4},
        )
        self.assertEqual(len(entries), 27)
        ids = {entry["id"] for entry in entries}
        self.assertNotIn("KB-003", ids)
        self.assertNotIn("KB-011", ids)
        self.assertNotIn("KB-032", ids)
        self.assertIn("KB-030", ids)
        self.assertIsNone(expired_context)
        self.assertIsNone(unrelated_deadline)

    def test_approved_row_requires_reviewer_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = Path(directory) / "queue.csv"
            output = Path(directory) / "approved.json"
            copy_queue_with_change(queue, "FAQ-001", "reviewer", "")
            with self.assertRaisesRegex(
                PromotionValidationError,
                "missing required field reviewer",
            ):
                promote_approved_knowledge(
                    queue_path=queue,
                    candidates_path=DEFAULT_CANDIDATES_PATH,
                    output_path=output,
                )

    def test_secret_or_wifi_password_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = Path(directory) / "queue.csv"
            output = Path(directory) / "approved.json"
            copy_queue_with_change(
                queue,
                "FAQ-033",
                "corrected_answer",
                "Wi-Fi " + "pass" + "word" + ": " + "blocked-value",
            )
            with self.assertRaisesRegex(
                PromotionValidationError,
                "contains PII or a secret",
            ):
                promote_approved_knowledge(
                    queue_path=queue,
                    candidates_path=DEFAULT_CANDIDATES_PATH,
                    output_path=output,
                )

    def test_approved_volatile_row_requires_current_valid_until(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = Path(directory) / "queue.csv"
            output = Path(directory) / "approved.json"
            copy_queue_with_change(
                queue,
                "FAQ-017",
                "valid_until",
                "2026-07-01",
            )
            with self.assertRaisesRegex(
                PromotionValidationError,
                "already expired",
            ):
                promote_approved_knowledge(
                    queue_path=queue,
                    candidates_path=DEFAULT_CANDIDATES_PATH,
                    output_path=output,
                )


if __name__ == "__main__":
    unittest.main()
