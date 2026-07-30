from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import _bootstrap  # noqa: F401

from handoff_store import (
    APPROVED_FOR_PUBLISH,
    PUBLISHED,
    REJECTED,
    create_handoff,
    get_knowledge_candidate,
    get_knowledge_candidate_for_handoff,
    initialize_store,
    resolve_handoff,
    review_knowledge_candidate,
)
from knowledge_publisher import (
    KnowledgePublishError,
    _normalize_canonical_question,
    publish_candidate,
)


class KnowledgePublisherHardeningTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_assistant.db"
        self.json_path = Path(self.temp_dir.name) / "labcoach-knowledge.json"
        self.base_path = Path(self.temp_dir.name) / "course-knowledge.json"

        initialize_store(self.db_path)

        # Create empty valid base knowledge file by default
        self.base_path.write_text(
            json.dumps({"schema_version": "1.0", "entries": []}),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_and_review_candidate(
        self,
        decision=APPROVED_FOR_PUBLISH,
        question="Buổi labcoach tiếp theo?",
        answer="Labcoach vào 20h tối mai trên kênh Discord.",
    ):
        rec = create_handoff(
            question=question,
            intent="logistics",
            reason="Hỏi lịch",
            trace_id=f"trace-{Path(tempfile.mktemp()).name}",
            model="gemini",
            learner_session_id="sess-PUB",
            db_path=self.db_path,
        )
        resolve_handoff(rec["handoff_id"], answer, db_path=self.db_path)
        cand = get_knowledge_candidate_for_handoff(rec["handoff_id"], db_path=self.db_path)

        if decision != "pending_review":
            review_knowledge_candidate(
                cand["candidate_id"],
                decision,
                question,
                answer,
                "TA Vũ",
                "Đã duyệt",
                db_path=self.db_path,
            )
        return get_knowledge_candidate(cand["candidate_id"], db_path=self.db_path)

    def test_target_json_corrupted_raises_error_and_preserves_file(self):
        # Target JSON is invalid syntax
        raw_bytes = b"BROKEN_JSON{{{"
        self.json_path.write_bytes(raw_bytes)

        cand = self._create_and_review_candidate()
        with self.assertRaises(KnowledgePublishError):
            publish_candidate(
                cand["candidate_id"],
                topic="schedule",
                volatile=False,
                knowledge_path=self.json_path,
                db_path=self.db_path,
                base_knowledge_path=self.base_path,
            )

        self.assertEqual(self.json_path.read_bytes(), raw_bytes)
        cand_after = get_knowledge_candidate(cand["candidate_id"], db_path=self.db_path)
        self.assertEqual(cand_after["review_status"], APPROVED_FOR_PUBLISH)

    def test_target_wrong_schema_version_is_not_overwritten(self):
        content = json.dumps({"schema_version": "9.9", "entries": []})
        self.json_path.write_text(content, encoding="utf-8")

        cand = self._create_and_review_candidate()
        with self.assertRaises(KnowledgePublishError):
            publish_candidate(
                cand["candidate_id"],
                topic="schedule",
                volatile=False,
                knowledge_path=self.json_path,
                db_path=self.db_path,
                base_knowledge_path=self.base_path,
            )

        self.assertEqual(self.json_path.read_text(encoding="utf-8"), content)

    def test_target_entries_not_list_is_not_overwritten(self):
        content = json.dumps({"schema_version": "1.0", "entries": "NOT_A_LIST"})
        self.json_path.write_text(content, encoding="utf-8")

        cand = self._create_and_review_candidate()
        with self.assertRaises(KnowledgePublishError):
            publish_candidate(
                cand["candidate_id"],
                topic="schedule",
                volatile=False,
                knowledge_path=self.json_path,
                db_path=self.db_path,
                base_knowledge_path=self.base_path,
            )

        self.assertEqual(self.json_path.read_text(encoding="utf-8"), content)

    def test_course_knowledge_corrupted_blocks_publish(self):
        self.base_path.write_text("CORRUPTED", encoding="utf-8")
        cand = self._create_and_review_candidate()

        with self.assertRaises(KnowledgePublishError):
            publish_candidate(
                cand["candidate_id"],
                topic="schedule",
                volatile=False,
                knowledge_path=self.json_path,
                db_path=self.db_path,
                base_knowledge_path=self.base_path,
            )

        self.assertFalse(self.json_path.exists())
        cand_after = get_knowledge_candidate(cand["candidate_id"], db_path=self.db_path)
        self.assertEqual(cand_after["review_status"], APPROVED_FOR_PUBLISH)

    def test_canonical_question_collision_with_course_knowledge_blocked(self):
        course_entry = {
            "id": "KB-001",
            "topic": "logistics",
            "canonical_question": "Lịch nghỉ Tết Nguyên Đán khi nào?",
            "question_variants": [],
            "answer": "Nghỉ từ 28 âm",
            "source_ids": ["IMG-001"],
            "source_type": "official",
            "authority": "verified",
            "volatile": False,
            "valid_until": None,
            "status": "approved",
            "verified_by": "Admin",
            "verified_at": "2026-01-01T00:00:00Z",
        }
        self.base_path.write_text(
            json.dumps({"schema_version": "1.0", "entries": [course_entry]}, ensure_ascii=False),
            encoding="utf-8",
        )

        cand = self._create_and_review_candidate(question="Lịch nghỉ Tết Nguyên Đán khi nào?")
        with self.assertRaises(KnowledgePublishError) as cm:
            publish_candidate(
                cand["candidate_id"],
                topic="schedule",
                volatile=False,
                knowledge_path=self.json_path,
                db_path=self.db_path,
                base_knowledge_path=self.base_path,
            )

        self.assertIn("gốc", str(cm.exception))
        self.assertFalse(self.json_path.exists())
        cand_after = get_knowledge_candidate(cand["candidate_id"], db_path=self.db_path)
        self.assertEqual(cand_after["review_status"], APPROVED_FOR_PUBLISH)

    def test_canonical_question_normalized_collision_blocked(self):
        # Collision after NFD accents removal, casefold, and whitespace collapsing
        course_entry = {
            "id": "KB-002",
            "topic": "logistics",
            "canonical_question": "Lịch  nghỉ  Tết  Nguyên  Đán?",
            "question_variants": [],
            "answer": "Nghỉ từ 28 âm",
            "source_ids": ["IMG-001"],
            "source_type": "official",
            "authority": "verified",
            "volatile": False,
            "valid_until": None,
            "status": "approved",
            "verified_by": "Admin",
            "verified_at": "2026-01-01T00:00:00Z",
        }
        self.base_path.write_text(
            json.dumps({"schema_version": "1.0", "entries": [course_entry]}, ensure_ascii=False),
            encoding="utf-8",
        )

        cand = self._create_and_review_candidate(question="lich nghi tet nguyen dan?")
        with self.assertRaises(KnowledgePublishError):
            publish_candidate(
                cand["candidate_id"],
                topic="schedule",
                volatile=False,
                knowledge_path=self.json_path,
                db_path=self.db_path,
                base_knowledge_path=self.base_path,
            )

    def test_canonical_question_collision_with_other_labcoach_entry_blocked(self):
        labcoach_entry = {
            "id": "KB-LC-OTHER",
            "topic": "schedule",
            "canonical_question": "Nộp bài tập ở đâu?",
            "question_variants": [],
            "answer": "Nộp qua LMS",
            "source_ids": ["HO-00000000"],
            "source_type": "labcoach_reviewed",
            "official_source": "Labcoach persistent queue",
            "authority": "verified",
            "volatile": False,
            "valid_until": None,
            "status": "approved",
            "verified_by": "TA Old",
            "verified_at": "2026-01-01T00:00:00Z",
        }
        self.json_path.write_text(
            json.dumps({"schema_version": "1.0", "entries": [labcoach_entry]}, ensure_ascii=False),
            encoding="utf-8",
        )

        cand = self._create_and_review_candidate(question="Nộp bài tập ở đâu?")
        with self.assertRaises(KnowledgePublishError) as cm:
            publish_candidate(
                cand["candidate_id"],
                topic="submission",
                volatile=False,
                knowledge_path=self.json_path,
                db_path=self.db_path,
                base_knowledge_path=self.base_path,
            )
        self.assertIn("target knowledge", str(cm.exception))

    def test_same_deterministic_id_updates_idempotently(self):
        cand = self._create_and_review_candidate(question="Câu hỏi duy nhất?")

        # First publish
        entry1 = publish_candidate(
            cand["candidate_id"],
            topic="topic1",
            volatile=False,
            knowledge_path=self.json_path,
            db_path=self.db_path,
            base_knowledge_path=self.base_path,
        )

        # Second publish (same candidate_id -> same KB-LC- deterministic ID)
        entry2 = publish_candidate(
            cand["candidate_id"],
            topic="topic2",
            volatile=False,
            knowledge_path=self.json_path,
            db_path=self.db_path,
            base_knowledge_path=self.base_path,
        )

        self.assertEqual(entry1["id"], entry2["id"])
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        self.assertEqual(len(data["entries"]), 1)
        self.assertEqual(data["entries"][0]["topic"], "topic2")

    def test_passing_course_path_as_target_is_blocked(self):
        cand = self._create_and_review_candidate()
        orig_content = self.base_path.read_text(encoding="utf-8")

        with self.assertRaises(KnowledgePublishError) as cm:
            publish_candidate(
                cand["candidate_id"],
                topic="schedule",
                volatile=False,
                knowledge_path=self.base_path,  # Passing base_path as target!
                db_path=self.db_path,
                base_knowledge_path=self.base_path,
            )

        self.assertIn("khóa học", str(cm.exception))
        self.assertEqual(self.base_path.read_text(encoding="utf-8"), orig_content)

    def test_temp_payload_failed_loader_validation_is_rejected(self):
        cand = self._create_and_review_candidate()
        orig_content = json.dumps({"schema_version": "1.0", "entries": []})
        self.json_path.write_text(orig_content, encoding="utf-8")

        # Mock load_approved_knowledge to return [] for temp file
        with patch("knowledge_publisher.load_approved_knowledge", return_value=[]):
            with self.assertRaises(KnowledgePublishError):
                publish_candidate(
                    cand["candidate_id"],
                    topic="schedule",
                    volatile=False,
                    knowledge_path=self.json_path,
                    db_path=self.db_path,
                    base_knowledge_path=self.base_path,
                )

        self.assertEqual(self.json_path.read_text(encoding="utf-8"), orig_content)
        cand_after = get_knowledge_candidate(cand["candidate_id"], db_path=self.db_path)
        self.assertEqual(cand_after["review_status"], APPROVED_FOR_PUBLISH)

    def test_valid_publish_succeeds(self):
        cand = self._create_and_review_candidate(question="Lịch phòng lab?")
        entry = publish_candidate(
            cand["candidate_id"],
            topic="schedule",
            volatile=False,
            knowledge_path=self.json_path,
            db_path=self.db_path,
            base_knowledge_path=self.base_path,
        )

        self.assertTrue(entry["id"].startswith("KB-LC-"))
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        self.assertEqual(len(data["entries"]), 1)

        cand_after = get_knowledge_candidate(cand["candidate_id"], db_path=self.db_path)
        self.assertEqual(cand_after["review_status"], PUBLISHED)

    def test_normalize_canonical_question_vietnamese_d(self):
        # "Đăng ký" and "dang ky" produce identical result
        self.assertEqual(
            _normalize_canonical_question("Đăng ký"),
            _normalize_canonical_question("dang ky"),
        )
        self.assertEqual(_normalize_canonical_question("Đăng ký"), "dang ky")

        # "Lịch nghỉ Tết Nguyên Đán?" and "lich nghi tet nguyen dan?" produce identical result
        self.assertEqual(
            _normalize_canonical_question("Lịch nghỉ Tết Nguyên Đán?"),
            _normalize_canonical_question("lich nghi tet nguyen dan?"),
        )
        self.assertEqual(
            _normalize_canonical_question("Lịch nghỉ Tết Nguyên Đán?"),
            "lich nghi tet nguyen dan?",
        )

        # Uppercase "Đ" is handled
        self.assertEqual(_normalize_canonical_question("ĐÀ NẴNG"), "da nang")

        # Multiple whitespace collapsed
        self.assertEqual(
            _normalize_canonical_question("  Đăng   ký   học  "),
            "dang ky hoc",
        )

        # Truly different questions remain different
        self.assertNotEqual(
            _normalize_canonical_question("Đăng ký học"),
            _normalize_canonical_question("Hủy đăng ký"),
        )


if __name__ == "__main__":
    unittest.main()
