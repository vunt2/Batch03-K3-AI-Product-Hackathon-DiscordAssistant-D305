from datetime import date
import unittest

import _bootstrap  # noqa: F401

from insight_service import build_daily_digest, cluster_handoffs


class InsightServiceTest(unittest.TestCase):
    def test_cluster_exact_normalized_questions(self):
        handoffs = [
            {
                "handoff_id": "HO-1",
                "question": "Lịch nghỉ Tết Nguyên Đán?",
                "intent": "logistics",
                "status": "pending",
                "created_at": "2026-07-31T01:00:00Z",
            },
            {
                "handoff_id": "HO-2",
                "question": "lich nghi tet nguyen dan?",
                "intent": "logistics",
                "status": "resolved",
                "created_at": "2026-07-31T02:00:00Z",
            },
        ]
        clusters = cluster_handoffs(handoffs)
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0]["count"], 2)
        self.assertEqual(clusters[0]["pending_count"], 1)
        self.assertEqual(clusters[0]["resolved_count"], 1)

    def test_vietnamese_accents_and_d_normalized(self):
        handoffs = [
            {"handoff_id": "HO-A", "question": "Đăng ký bảo lưu học phần"},
            {"handoff_id": "HO-B", "question": "dang ky bao luu hoc phan"},
        ]
        clusters = cluster_handoffs(handoffs)
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0]["count"], 2)

    def test_similar_questions_above_jaccard_threshold_clustered(self):
        handoffs = [
            {"handoff_id": "HO-11", "question": "Hạn nộp báo cáo tuần 3 là khi nào"},
            {"handoff_id": "HO-12", "question": "Khi nào hạn nộp báo cáo tuần 3"},
        ]
        clusters = cluster_handoffs(handoffs, similarity_threshold=0.6)
        self.assertEqual(len(clusters), 1)

    def test_different_topic_questions_not_clustered(self):
        handoffs = [
            {"handoff_id": "HO-21", "question": "Cách cài đặt Git trên Windows"},
            {"handoff_id": "HO-22", "question": "Lịch chấm thi giữa kỳ"},
        ]
        clusters = cluster_handoffs(handoffs)
        self.assertEqual(clusters, [])

    def test_stopwords_only_similarity_not_clustered(self):
        handoffs = [
            {"handoff_id": "HO-31", "question": "bạn ơi cho mình hỏi là cái gì thế"},
            {"handoff_id": "HO-32", "question": "cho mình hỏi bạn là thế nào ạ"},
        ]
        clusters = cluster_handoffs(handoffs)
        self.assertEqual(clusters, [])

    def test_clustering_is_deterministic(self):
        handoffs = [
            {"handoff_id": "HO-B", "question": "Hỏi deadline nộp bài", "created_at": "2026-07-31T02:00:00Z"},
            {"handoff_id": "HO-A", "question": "Hỏi deadline nộp bài", "created_at": "2026-07-31T01:00:00Z"},
        ]
        res1 = cluster_handoffs(handoffs)
        res2 = cluster_handoffs(list(reversed(handoffs)))
        self.assertEqual(res1, res2)

    def test_only_count_gte_2_is_repeated_cluster(self):
        handoffs = [
            {"handoff_id": "HO-UNIQUE", "question": "Câu hỏi hoàn toàn độc nhất duy nhất"},
        ]
        clusters = cluster_handoffs(handoffs)
        self.assertEqual(clusters, [])

    def test_daily_digest_bangkok_timezone_filtering(self):
        # 2026-07-30 20:00:00 UTC == 2026-07-31 03:00:00 Asia/Bangkok
        handoffs = [
            {
                "handoff_id": "HO-BK1",
                "question": "Hỏi câu 1",
                "created_at": "2026-07-30T20:00:00Z",
                "status": "pending",
            },
            {
                "handoff_id": "HO-PREV",
                "question": "Hỏi câu 2",
                "created_at": "2026-07-30T10:00:00Z",  # 17:00 Bangkok on 2026-07-30
                "status": "pending",
            },
        ]
        digest = build_daily_digest(handoffs, date(2026, 7, 31))
        self.assertEqual(digest["selected_date"], "2026-07-31")
        self.assertEqual(digest["total_questions"], 1)
        self.assertEqual(digest["pending_questions"][0]["handoff_id"], "HO-BK1")

    def test_daily_digest_malformed_timestamp_skipped_safely(self):
        handoffs = [
            {"handoff_id": "HO-BAD", "question": "Test", "created_at": "INVALID_TS"},
        ]
        digest = build_daily_digest(handoffs, date(2026, 7, 31))
        self.assertEqual(digest["total_questions"], 0)

    def test_pending_questions_have_no_fake_answers(self):
        handoffs = [
            {
                "handoff_id": "HO-P1",
                "question": "Chưa được giải đáp?",
                "reason": "Rationale test reason",
                "status": "pending",
                "created_at": "2026-07-31T01:00:00Z",
            }
        ]
        digest = build_daily_digest(handoffs, date(2026, 7, 31))
        self.assertEqual(len(digest["pending_questions"]), 1)
        self.assertNotIn("answer", digest["pending_questions"][0])
        self.assertNotIn("Rationale test reason", digest["markdown"])

    def test_resolved_items_use_actual_labcoach_response(self):
        handoffs = [
            {
                "handoff_id": "HO-R1",
                "question": "Lịch nộp bài?",
                "labcoach_response": "Nộp trước 23:59 chủ nhật",
                "status": "resolved",
                "created_at": "2026-07-31T01:00:00Z",
            }
        ]
        digest = build_daily_digest(handoffs, date(2026, 7, 31))
        self.assertEqual(len(digest["resolved_items"]), 1)
        self.assertEqual(digest["resolved_items"][0]["answer"], "Nộp trước 23:59 chủ nhật")
        self.assertIn("Nộp trước 23:59 chủ nhật", digest["markdown"])

    def test_secrets_redacted_in_questions_and_responses(self):
        handoffs = [
            {
                "handoff_id": "HO-SEC",
                "question": "Key AIzaSySecretKey9999999999991111 dùng thế nào?",
                "labcoach_response": "Dùng secret_token_1234567890_abc để auth",
                "status": "resolved",
                "created_at": "2026-07-31T01:00:00Z",
            }
        ]
        digest = build_daily_digest(handoffs, date(2026, 7, 31))
        self.assertNotIn("AIzaSySecretKey9999999999991111", digest["markdown"])
        self.assertNotIn("secret_token_1234567890_abc", digest["markdown"])
        self.assertIn("[REDACTED]", digest["markdown"])

    def test_daily_digest_limits_enforced(self):
        handoffs = []
        for i in range(30):
            handoffs.append(
                {
                    "handoff_id": f"HO-P-{i:02d}",
                    "question": f"Pending question number {i}",
                    "status": "pending",
                    "created_at": "2026-07-31T01:00:00Z",
                }
            )
            handoffs.append(
                {
                    "handoff_id": f"HO-R-{i:02d}",
                    "question": f"Resolved question number {i}",
                    "labcoach_response": f"Response {i}",
                    "status": "resolved",
                    "created_at": "2026-07-31T02:00:00Z",
                }
            )

        digest = build_daily_digest(handoffs, date(2026, 7, 31))
        self.assertEqual(digest["total_questions"], 60)
        self.assertEqual(len(digest["pending_questions"]), 20)
        self.assertEqual(len(digest["resolved_items"]), 20)

    def test_empty_input_returns_valid_digest(self):
        digest = build_daily_digest([], date(2026, 7, 31))
        self.assertEqual(digest["total_questions"], 0)
        self.assertEqual(digest["pending_count"], 0)
        self.assertEqual(digest["resolved_count"], 0)
        self.assertEqual(digest["repeated_cluster_count"], 0)
        self.assertIn("# BÁO CÁO TỔNG HỢP LABCOACH - 2026-07-31", digest["markdown"])


if __name__ == "__main__":
    unittest.main()
