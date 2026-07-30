from datetime import date
import json
from pathlib import Path
import tempfile
import unittest

import _bootstrap  # noqa: F401

from knowledge_base import (
    load_approved_knowledge,
    retrieve_approved_match,
)


TODAY = date(2026, 7, 30)


def approved_entry(**overrides):
    entry = {
        "id": "KB-TEST",
        "topic": "submission",
        "canonical_question": "Nộp weekly report ở đâu?",
        "question_variants": ["Weekly submit như thế nào?"],
        "answer": "Dùng lệnh weekly trong kênh của team.",
        "source_image_ids": ["IMG-010"],
        "source_type": "official",
        "authority": "verified",
        "volatile": False,
        "valid_until": None,
        "status": "approved",
        "verified_by": "REVIEWER-001",
        "verified_at": "2026-07-30T10:00:00Z",
    }
    entry.update(overrides)
    return entry


def write_store(path: Path, entries):
    path.write_text(
        json.dumps(
            {"schema_version": "1.0", "entries": entries},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


class KnowledgeBaseTest(unittest.TestCase):
    def test_required_retrieval_cases(self):
        cases = (
            ("Nhà ăn đóng cửa lúc mấy giờ?", None),
            ("Deadline tạo team là khi nào?", None),
            ("Lớp mình mấy giờ bắt đầu học buổi tiếp theo ạ?", None),
            ("Buổi học tiếp theo bắt đầu lúc nào?", None),
            ("Các hoạt động buổi tối bắt đầu lúc mấy giờ?", "KB-014"),
            ("Buổi tối có hoạt động online không?", "KB-014"),
            ("Mentor Duty diễn ra khi nào?", "KB-030"),
            ("Một người hay cả team nộp weekly report?", "KB-013"),
            ("Weekly report cần nộp nội dung gì?", "KB-006"),
        )
        for question, expected_id in cases:
            with self.subTest(question=question):
                match = retrieve_approved_match(question, today=TODAY)
                actual_id = match["knowledge_id"] if match else None
                self.assertEqual(actual_id, expected_id)

    def test_match_returns_source_metadata(self):
        match = retrieve_approved_match(
            "Weekly report cần nộp nội dung gì?",
            today=TODAY,
        )
        self.assertIsNotNone(match)
        self.assertEqual(match["knowledge_id"], "KB-006")
        self.assertEqual(
            match["source_ids"],
            ["IMG-010", "IMG-013", "IMG-029"],
        )
        self.assertEqual(match["topic"], "submission")
        self.assertTrue(match["source_verified"])

    def test_expired_volatile_entry_is_not_loaded_or_retrieved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "approved.json"
            write_store(
                path,
                [
                    approved_entry(
                        volatile=True,
                        valid_until="2026-07-01",
                    )
                ],
            )
            entries = load_approved_knowledge(path, today=TODAY)
            match = retrieve_approved_match(
                "Weekly submit như thế nào?",
                path,
                today=TODAY,
            )
        self.assertEqual(entries, [])
        self.assertIsNone(match)

    def test_unapproved_or_unverified_entries_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "approved.json"
            write_store(
                path,
                [
                    approved_entry(status="needs_review"),
                    approved_entry(
                        id="KB-OTHER",
                        canonical_question="Một câu khác",
                        authority="unknown",
                    ),
                ],
            )
            entries = load_approved_knowledge(path, today=TODAY)
        self.assertEqual(entries, [])

    def test_invalid_json_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "approved.json"
            path.write_text("{invalid", encoding="utf-8")
            self.assertEqual(load_approved_knowledge(path), [])
            self.assertIsNone(
                retrieve_approved_match("Weekly report", path)
            )

    def test_pii_entry_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "approved.json"
            write_store(
                path,
                [approved_entry(answer="Liên hệ learner@example.com.")],
            )
            entries = load_approved_knowledge(path, today=TODAY)
        self.assertEqual(entries, [])


if __name__ == "__main__":
    unittest.main()
