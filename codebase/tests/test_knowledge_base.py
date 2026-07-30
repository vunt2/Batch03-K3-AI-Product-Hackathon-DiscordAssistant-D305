from datetime import date
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

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
            (
                "Chương trình Build Phase diễn ra trong bao lâu?",
                "KB-LC-34781B3C",
            ),
            ("Build Phase kéo dài mấy tuần?", "KB-LC-34781B3C"),
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

    def test_loader_supports_new_source_ids_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "labcoach-knowledge.json"
            write_store(
                path,
                [
                    {
                        "id": "KB-LC-001",
                        "topic": "logistics",
                        "canonical_question": "Buổi học labcoach diễn ra ở đâu?",
                        "question_variants": [],
                        "answer": "Học online trên Discord.",
                        "source_ids": ["HO-ABC12345"],
                        "source_type": "labcoach_reviewed",
                        "authority": "verified",
                        "volatile": False,
                        "valid_until": None,
                        "status": "approved",
                        "verified_by": "TA Vũ",
                        "verified_at": "2026-07-30T10:00:00Z",
                    }
                ],
            )
            entries = load_approved_knowledge(path, today=TODAY)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["source_ids"], ["HO-ABC12345"])

            match = retrieve_approved_match(
                "Buổi học labcoach diễn ra ở đâu?", path, today=TODAY
            )
            self.assertIsNotNone(match)
            self.assertEqual(match["knowledge_id"], "KB-LC-001")
            self.assertEqual(match["source_ids"], ["HO-ABC12345"])

    def test_loader_merges_course_and_labcoach_files_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            course_path = Path(directory) / "course-knowledge.json"
            labcoach_path = Path(directory) / "labcoach-knowledge.json"

            write_store(
                course_path,
                [
                    approved_entry(id="KB-001", canonical_question="Hỏi câu 1"),
                ],
            )
            write_store(
                labcoach_path,
                [
                    approved_entry(id="KB-001", canonical_question="Hỏi trùng ID"),
                    approved_entry(id="KB-LC-002", canonical_question="Hỏi câu 1"),
                    approved_entry(
                        id="KB-LC-003",
                        canonical_question="Hỏi câu 3 duy nhất",
                        source_image_ids=None,
                        source_ids=["HO-99999999"],
                    ),
                ],
            )

            with patch("knowledge_base.APPROVED_KNOWLEDGE_PATH", course_path), patch(
                "knowledge_base.LABCOACH_APPROVED_KNOWLEDGE_PATH", labcoach_path
            ):
                entries = load_approved_knowledge(today=TODAY)
                self.assertEqual(len(entries), 2)
                ids = {e["id"] for e in entries}
                self.assertEqual(ids, {"KB-001", "KB-LC-003"})

    def test_explicit_path_loads_single_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "custom.json"
            write_store(path, [approved_entry(id="KB-CUSTOM")])
            entries = load_approved_knowledge(path, today=TODAY)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["id"], "KB-CUSTOM")

    def test_missing_or_corrupt_labcoach_file_does_not_break_loader(self):
        with tempfile.TemporaryDirectory() as directory:
            course_path = Path(directory) / "course-knowledge.json"
            labcoach_path = Path(directory) / "nonexistent-labcoach.json"

            write_store(course_path, [approved_entry(id="KB-CORE")])

            with patch("knowledge_base.APPROVED_KNOWLEDGE_PATH", course_path), patch(
                "knowledge_base.LABCOACH_APPROVED_KNOWLEDGE_PATH", labcoach_path
            ):
                entries = load_approved_knowledge(today=TODAY)
                self.assertEqual(len(entries), 1)
                self.assertEqual(entries[0]["id"], "KB-CORE")


if __name__ == "__main__":
    unittest.main()
