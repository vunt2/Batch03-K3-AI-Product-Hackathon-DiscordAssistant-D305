import concurrent.futures
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import warnings

import _bootstrap  # noqa: F401

from handoff_store import (
    APPROVED_FOR_PUBLISH,
    PENDING,
    PENDING_REVIEW,
    REJECTED,
    RESOLVED,
    StoreError,
    count_handoffs,
    count_knowledge_candidates,
    create_handoff,
    delete_session_handoffs,
    get_handoff,
    get_knowledge_candidate_for_handoff,
    initialize_store,
    list_handoffs,
    list_knowledge_candidates,
    list_session_handoffs,
    reopen_handoff,
    resolve_db_path,
    resolve_handoff,
    review_knowledge_candidate,
)


class HandoffStoreTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_assistant.db"

    def tearDown(self):
        # On Windows, this cleanup will fail with PermissionError if connection is unclosed
        self.temp_dir.cleanup()

    def test_initialize_schema_multiple_times(self):
        res1 = initialize_store(self.db_path)
        res2 = initialize_store(self.db_path)
        self.assertEqual(res1, res2)
        self.assertTrue(self.db_path.exists())

    def test_no_resource_warning_on_operations(self):
        with warnings.catch_warnings(record=True) as recorded_warnings:
            warnings.simplefilter("always", ResourceWarning)
            initialize_store(self.db_path)
            rec = create_handoff(
                question="Test question",
                intent="logistics",
                reason="Reason",
                trace_id="tr-1",
                model="m",
                learner_session_id="s-1",
                db_path=self.db_path,
            )
            get_handoff(rec["handoff_id"], db_path=self.db_path)
            count_handoffs(db_path=self.db_path)
            resolve_handoff(rec["handoff_id"], "Answer", db_path=self.db_path)
            reopen_handoff(rec["handoff_id"], db_path=self.db_path)
            delete_session_handoffs("s-1", db_path=self.db_path)

        unclosed_warnings = [
            w for w in recorded_warnings if "unclosed" in str(w.message).lower()
        ]
        self.assertEqual(len(unclosed_warnings), 0)

    def test_create_and_load_by_new_connection(self):
        record = create_handoff(
            question="Weekly report cần nộp gì?",
            intent="logistics",
            reason="Thiếu thông tin",
            trace_id="trace-001",
            model="gemini-3.5-flash-lite",
            learner_session_id="sess-A",
            db_path=self.db_path,
        )
        self.assertTrue(record["handoff_id"].startswith("HO-"))
        self.assertEqual(record["status"], PENDING)

        loaded = get_handoff(record["handoff_id"], db_path=self.db_path)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["question"], "Weekly report cần nộp gì?")
        self.assertEqual(loaded["learner_session_id"], "sess-A")

    def test_dedupe_same_trace_id_concurrent(self):
        def _call():
            return create_handoff(
                question="Deadline CP3 khi nào?",
                intent="logistics",
                reason="Reason",
                trace_id="concurrent-trace",
                model="gemini",
                learner_session_id="sess-A",
                db_path=self.db_path,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(_call) for _ in range(4)]
            results = [f.result() for f in futures]

        handoff_ids = {r["handoff_id"] for r in results}
        self.assertEqual(len(handoff_ids), 1)

    def test_dedupe_same_session_normalized_question_pending_concurrent(self):
        def _call():
            return create_handoff(
                question="  Deadline  CP3 khi NÀO?  ",
                intent="logistics",
                reason="Reason",
                trace_id="",
                model="gemini",
                learner_session_id="sess-A",
                db_path=self.db_path,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(_call) for _ in range(4)]
            results = [f.result() for f in futures]

        handoff_ids = {r["handoff_id"] for r in results}
        self.assertEqual(len(handoff_ids), 1)

    def test_allow_same_question_across_different_sessions(self):
        r1 = create_handoff(
            question="Lịch mentor duty?",
            intent="logistics",
            reason="Reason 1",
            trace_id="trace-201",
            model="gemini",
            learner_session_id="sess-A",
            db_path=self.db_path,
        )
        r2 = create_handoff(
            question="Lịch mentor duty?",
            intent="logistics",
            reason="Reason 2",
            trace_id="trace-202",
            model="gemini",
            learner_session_id="sess-B",
            db_path=self.db_path,
        )
        self.assertNotEqual(r1["handoff_id"], r2["handoff_id"])

    def test_resolve_allows_new_pending_for_same_question(self):
        r1 = create_handoff(
            question="Lịch nghỉ hè?",
            intent="logistics",
            reason="Reason 1",
            trace_id="tr-a",
            model="gemini",
            learner_session_id="sess-A",
            db_path=self.db_path,
        )
        resolve_handoff(r1["handoff_id"], "Nghỉ từ tuần sau.", db_path=self.db_path)

        r2 = create_handoff(
            question="Lịch nghỉ hè?",
            intent="logistics",
            reason="Reason 2",
            trace_id="tr-b",
            model="gemini",
            learner_session_id="sess-A",
            db_path=self.db_path,
        )
        self.assertNotEqual(r1["handoff_id"], r2["handoff_id"])
        self.assertEqual(r2["status"], PENDING)

    def test_reopen_conflict_handled_gracefully(self):
        # Create r1 and resolve it
        r1 = create_handoff(
            question="Hạn chót CP4?",
            intent="logistics",
            reason="R1",
            trace_id="t1",
            model="m",
            learner_session_id="sess-X",
            db_path=self.db_path,
        )
        resolve_handoff(r1["handoff_id"], "Đã xong", db_path=self.db_path)

        # Create r2 for same question while r1 is resolved
        create_handoff(
            question="Hạn chót CP4?",
            intent="logistics",
            reason="R2",
            trace_id="t2",
            model="m",
            learner_session_id="sess-X",
            db_path=self.db_path,
        )

        # Reopening r1 now conflicts with r2 pending
        ok = reopen_handoff(r1["handoff_id"], db_path=self.db_path)
        self.assertFalse(ok)

    def test_invalid_input_validation(self):
        with self.assertRaises(StoreError):
            create_handoff(
                question="   ",
                intent="logistics",
                reason="R",
                trace_id="t",
                model="m",
                learner_session_id="sess-1",
                db_path=self.db_path,
            )
        with self.assertRaises(StoreError):
            create_handoff(
                question="Q",
                intent="logistics",
                reason="R",
                trace_id="t",
                model="m",
                learner_session_id="",
                db_path=self.db_path,
            )

    def test_sqlite_error_converts_to_store_error(self):
        bad_path = Path(self.temp_dir.name) / "nonexistent_dir" / "readonly_file"
        # Create a directory named readonly_file so sqlite connect fails
        bad_path.mkdir(parents=True)
        with self.assertRaises(StoreError) as cm:
            initialize_store(bad_path)
        self.assertIn("Không thể truy cập kho handoff", str(cm.exception))

    def test_db_usable_after_transaction_error(self):
        # Trigger an error safely and ensure db can continue to be used
        create_handoff(
            question="Q1",
            intent="logistics",
            reason="R",
            trace_id="t1",
            model="m",
            learner_session_id="s1",
            db_path=self.db_path,
        )
        p, r = count_handoffs(db_path=self.db_path)
        self.assertEqual(p, 1)

    def test_resolve_handoff_creates_single_pending_review_candidate(self):
        rec = create_handoff(
            question="Buổi học tiếp theo lúc mấy giờ?",
            intent="logistics",
            reason="Cần thông tin",
            trace_id="kc-tr-1",
            model="gemini",
            learner_session_id="sess-KC1",
            db_path=self.db_path,
        )
        ok = resolve_handoff(
            rec["handoff_id"],
            "Buổi học tiếp theo bắt đầu lúc 19:30.",
            db_path=self.db_path,
        )
        self.assertTrue(ok)

        cand = get_knowledge_candidate_for_handoff(
            rec["handoff_id"], db_path=self.db_path
        )
        self.assertIsNotNone(cand)
        self.assertTrue(cand["candidate_id"].startswith("KC-"))
        self.assertEqual(cand["handoff_id"], rec["handoff_id"])
        self.assertEqual(cand["question"], "Buổi học tiếp theo lúc mấy giờ?")
        self.assertEqual(
            cand["answer"], "Buổi học tiếp theo bắt đầu lúc 19:30."
        )
        self.assertEqual(cand["intent"], "logistics")
        self.assertEqual(cand["source_type"], "labcoach_response")
        self.assertEqual(cand["review_status"], "pending_review")

        cands = list_knowledge_candidates("pending_review", db_path=self.db_path)
        self.assertEqual(len(cands), 1)

    def test_resolve_again_updates_candidate_without_duplicate(self):
        rec = create_handoff(
            question="Địa điểm học trực tiếp?",
            intent="logistics",
            reason="Cần địa điểm",
            trace_id="kc-tr-2",
            model="gemini",
            learner_session_id="sess-KC2",
            db_path=self.db_path,
        )
        resolve_handoff(
            rec["handoff_id"], "Phòng 301 nhà A", db_path=self.db_path
        )
        cand1 = get_knowledge_candidate_for_handoff(
            rec["handoff_id"], db_path=self.db_path
        )

        resolve_handoff(
            rec["handoff_id"], "Phòng 402 nhà B", db_path=self.db_path
        )
        cand2 = get_knowledge_candidate_for_handoff(
            rec["handoff_id"], db_path=self.db_path
        )

        self.assertEqual(cand1["candidate_id"], cand2["candidate_id"])
        self.assertEqual(cand2["answer"], "Phòng 402 nhà B")

        cands = list_knowledge_candidates(db_path=self.db_path)
        self.assertEqual(len(cands), 1)

    def test_delete_session_handoffs_preserves_candidates(self):
        rec = create_handoff(
            question="Link nộp bài?",
            intent="logistics",
            reason="Cần link",
            trace_id="kc-tr-3",
            model="gemini",
            learner_session_id="sess-TO_DELETE",
            db_path=self.db_path,
        )
        resolve_handoff(
            rec["handoff_id"], "Link nộp bài tại lms.example.com", db_path=self.db_path
        )

        deleted_count = delete_session_handoffs("sess-TO_DELETE", db_path=self.db_path)
        self.assertEqual(deleted_count, 1)

        # Handoff is gone
        self.assertIsNone(get_handoff(rec["handoff_id"], db_path=self.db_path))

        # Candidate is STILL present for audit/review
        cand = get_knowledge_candidate_for_handoff(
            rec["handoff_id"], db_path=self.db_path
        )
        self.assertIsNotNone(cand)
        self.assertEqual(cand["answer"], "Link nộp bài tại lms.example.com")

    def test_sensitive_data_redacted_in_candidate(self):
        rec = create_handoff(
            question="Dùng API Key AIzaSyDummyKey12345678901234567890 này sao?",
            intent="technical_setup",
            reason="Hỏi key",
            trace_id="kc-tr-4",
            model="gemini",
            learner_session_id="sess-KC4",
            db_path=self.db_path,
        )
        resolve_handoff(
            rec["handoff_id"],
            "Cấu hình GEMINI_API_KEY=AIzaSySecretKey999999999999 trong .env",
            db_path=self.db_path,
        )

        cand = get_knowledge_candidate_for_handoff(
            rec["handoff_id"], db_path=self.db_path
        )
        self.assertIsNotNone(cand)
        self.assertNotIn("AIzaSyDummyKey12345678901234567890", cand["question"])
        self.assertNotIn("AIzaSySecretKey999999999999", cand["answer"])
        self.assertIn("[REDACTED]", cand["question"])
        self.assertIn("[REDACTED]", cand["answer"])

    def test_resolve_transaction_atomicity_on_failure(self):
        rec = create_handoff(
            question="Khi nào nộp bài?",
            intent="logistics",
            reason="Hỏi hạn",
            trace_id="atomicity-trace",
            model="gemini",
            learner_session_id="sess-ATOM",
            db_path=self.db_path,
        )

        # Attach temporary SQLite trigger to force candidate INSERT failure
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TRIGGER force_candidate_insert_failure
            BEFORE INSERT ON knowledge_candidates
            BEGIN
                SELECT RAISE(ABORT, 'forced candidate failure');
            END;
            """
        )
        conn.commit()
        conn.close()

        try:
            with self.assertRaises(StoreError):
                resolve_handoff(
                    rec["handoff_id"],
                    "Hạn nộp vào 23:59 chủ nhật.",
                    db_path=self.db_path,
                )
        finally:
            conn_cleanup = sqlite3.connect(self.db_path)
            conn_cleanup.execute(
                "DROP TRIGGER IF EXISTS force_candidate_insert_failure;"
            )
            conn_cleanup.commit()
            conn_cleanup.close()

        # Assert full rollback occurred
        handoff_after = get_handoff(rec["handoff_id"], db_path=self.db_path)
        self.assertIsNotNone(handoff_after)
        self.assertEqual(handoff_after["status"], PENDING)
        self.assertEqual(handoff_after["labcoach_response"], "")
        self.assertIsNone(handoff_after["resolved_at"])

        cand = get_knowledge_candidate_for_handoff(
            rec["handoff_id"], db_path=self.db_path
        )
        self.assertIsNone(cand)

    def test_schema_migration_on_old_candidate_table(self):
        # Create old schema table without review columns
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE knowledge_candidates (
                candidate_id TEXT PRIMARY KEY,
                handoff_id TEXT NOT NULL UNIQUE,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                intent TEXT NOT NULL,
                source_type TEXT NOT NULL,
                review_status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            INSERT INTO knowledge_candidates VALUES (
                'KC-OLD', 'HO-OLD', 'Old Q?', 'Old A', 'logistics',
                'labcoach_response', 'pending_review', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z'
            );
            """
        )
        conn.commit()
        conn.close()

        # Run initialize_store to perform migration
        initialize_store(self.db_path)

        # Run initialize_store again to ensure idempotency
        initialize_store(self.db_path)

        cand = get_knowledge_candidate_for_handoff("HO-OLD", db_path=self.db_path)
        self.assertIsNotNone(cand)
        self.assertEqual(cand["candidate_id"], "KC-OLD")
        self.assertEqual(cand["reviewed_by"], "")
        self.assertIsNone(cand["reviewed_at"])
        self.assertEqual(cand["review_note"], "")

    def test_review_knowledge_candidate_approve(self):
        rec = create_handoff(
            question="Lịch nghỉ tết?",
            intent="logistics",
            reason="Hỏi tết",
            trace_id="tr-rev-1",
            model="gemini",
            learner_session_id="sess-REV1",
            db_path=self.db_path,
        )
        resolve_handoff(rec["handoff_id"], "Nghỉ từ 28 âm lịch", db_path=self.db_path)
        cand = get_knowledge_candidate_for_handoff(rec["handoff_id"], db_path=self.db_path)

        ok = review_knowledge_candidate(
            candidate_id=cand["candidate_id"],
            decision=APPROVED_FOR_PUBLISH,
            edited_question="Lịch nghỉ Tết Nguyên Đán là khi nào?",
            edited_answer="Lịch nghỉ bắt đầu từ 28 âm lịch.",
            reviewer="Nguyễn Tuấn Vũ",
            review_note="Đã xác minh với BTC",
            db_path=self.db_path,
        )
        self.assertTrue(ok)

        cand_after = get_knowledge_candidate_for_handoff(rec["handoff_id"], db_path=self.db_path)
        self.assertEqual(cand_after["review_status"], APPROVED_FOR_PUBLISH)
        self.assertEqual(cand_after["question"], "Lịch nghỉ Tết Nguyên Đán là khi nào?")
        self.assertEqual(cand_after["answer"], "Lịch nghỉ bắt đầu từ 28 âm lịch.")
        self.assertEqual(cand_after["reviewed_by"], "Nguyễn Tuấn Vũ")
        self.assertIsNotNone(cand_after["reviewed_at"])
        self.assertEqual(cand_after["review_note"], "Đã xác minh với BTC")

        p, a, r = count_knowledge_candidates(db_path=self.db_path)
        self.assertEqual(p, 0)
        self.assertEqual(a, 1)
        self.assertEqual(r, 0)

    def test_review_knowledge_candidate_reject(self):
        rec = create_handoff(
            question="Cho em xin đề thi?",
            intent="learning",
            reason="Hỏi đề",
            trace_id="tr-rev-2",
            model="gemini",
            learner_session_id="sess-REV2",
            db_path=self.db_path,
        )
        resolve_handoff(rec["handoff_id"], "Không chia sẻ đề", db_path=self.db_path)
        cand = get_knowledge_candidate_for_handoff(rec["handoff_id"], db_path=self.db_path)

        ok = review_knowledge_candidate(
            candidate_id=cand["candidate_id"],
            decision=REJECTED,
            edited_question="Cho em xin đề thi?",
            edited_answer="Không chia sẻ đề thi theo quy định.",
            reviewer="TA Phong",
            db_path=self.db_path,
        )
        self.assertTrue(ok)

        cand_after = get_knowledge_candidate_for_handoff(rec["handoff_id"], db_path=self.db_path)
        self.assertEqual(cand_after["review_status"], REJECTED)
        self.assertEqual(cand_after["reviewed_by"], "TA Phong")

    def test_review_knowledge_candidate_invalid_inputs(self):
        rec = create_handoff(
            question="Hạn nộp báo cáo?",
            intent="logistics",
            reason="Hỏi hạn",
            trace_id="tr-rev-3",
            model="gemini",
            learner_session_id="sess-REV3",
            db_path=self.db_path,
        )
        resolve_handoff(rec["handoff_id"], "Hạn vào cuối tuần", db_path=self.db_path)
        cand = get_knowledge_candidate_for_handoff(rec["handoff_id"], db_path=self.db_path)
        cid = cand["candidate_id"]

        # Invalid decision
        self.assertFalse(
            review_knowledge_candidate(cid, "invalid_status", "Q", "A", "Rev", db_path=self.db_path)
        )
        # Empty reviewer
        self.assertFalse(
            review_knowledge_candidate(cid, APPROVED_FOR_PUBLISH, "Q", "A", "   ", db_path=self.db_path)
        )
        # Empty question / answer
        self.assertFalse(
            review_knowledge_candidate(cid, APPROVED_FOR_PUBLISH, "  ", "A", "Rev", db_path=self.db_path)
        )
        self.assertFalse(
            review_knowledge_candidate(cid, APPROVED_FOR_PUBLISH, "Q", "  ", "Rev", db_path=self.db_path)
        )

    def test_review_knowledge_candidate_redacts_secrets(self):
        rec = create_handoff(
            question="Q", intent="i", reason="r", trace_id="tr-rev-4", model="m", learner_session_id="s4", db_path=self.db_path
        )
        resolve_handoff(rec["handoff_id"], "A", db_path=self.db_path)
        cand = get_knowledge_candidate_for_handoff(rec["handoff_id"], db_path=self.db_path)

        review_knowledge_candidate(
            cand["candidate_id"],
            APPROVED_FOR_PUBLISH,
            edited_question="Key AIzaSySecretKey9999999999991111?",
            edited_answer="Dùng Bearer secret_token_1234567890_abc",
            reviewer="Admin",
            review_note="Ghi chú chứa password=mysecretpass123",
            db_path=self.db_path,
        )

        cand_after = get_knowledge_candidate_for_handoff(rec["handoff_id"], db_path=self.db_path)
        self.assertNotIn("AIzaSySecretKey9999999999991111", cand_after["question"])
        self.assertNotIn("secret_token_1234567890_abc", cand_after["answer"])
        self.assertNotIn("mysecretpass123", cand_after["review_note"])
        self.assertIn("[REDACTED]", cand_after["question"])
        self.assertIn("[REDACTED]", cand_after["answer"])
        self.assertIn("[REDACTED]", cand_after["review_note"])

    def test_resolve_again_resets_approved_candidate_to_pending_review(self):
        rec = create_handoff(
            question="Lịch Mentor?",
            intent="logistics",
            reason="r",
            trace_id="tr-rev-5",
            model="m",
            learner_session_id="s5",
            db_path=self.db_path,
        )
        resolve_handoff(rec["handoff_id"], "Thứ hai hàng tuần", db_path=self.db_path)
        cand1 = get_knowledge_candidate_for_handoff(rec["handoff_id"], db_path=self.db_path)

        # Review and approve candidate
        review_knowledge_candidate(
            cand1["candidate_id"],
            APPROVED_FOR_PUBLISH,
            "Lịch Mentor?",
            "Thứ hai hàng tuần",
            "Reviewer A",
            "Approved note",
            db_path=self.db_path,
        )
        cand_approved = get_knowledge_candidate_for_handoff(rec["handoff_id"], db_path=self.db_path)
        self.assertEqual(cand_approved["review_status"], APPROVED_FOR_PUBLISH)

        # Resolve handoff again with new response
        resolve_handoff(rec["handoff_id"], "Đổi sang Thứ tư hàng tuần", db_path=self.db_path)

        cand_re_resolved = get_knowledge_candidate_for_handoff(rec["handoff_id"], db_path=self.db_path)
        self.assertEqual(cand_re_resolved["candidate_id"], cand1["candidate_id"])
        self.assertEqual(cand_re_resolved["answer"], "Đổi sang Thứ tư hàng tuần")
        self.assertEqual(cand_re_resolved["review_status"], PENDING_REVIEW)
        self.assertEqual(cand_re_resolved["reviewed_by"], "")
        self.assertIsNone(cand_re_resolved["reviewed_at"])
        self.assertEqual(cand_re_resolved["review_note"], "")


if __name__ == "__main__":
    unittest.main()
