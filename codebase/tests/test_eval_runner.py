import csv
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import _bootstrap  # noqa: F401

from model_client import GeminiConfig


class EvalRunnerSafetyTest(unittest.TestCase):
    def setUp(self):
        import sys

        root = Path(__file__).resolve().parents[2]
        eval_dir = root / "eval"
        if str(eval_dir) not in sys.path:
            sys.path.insert(0, str(eval_dir))
        from run_eval import run_evaluation

        self.run_evaluation = run_evaluation

    def test_eval_requires_successful_smoke_test(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(
                RuntimeError,
                "successful Gemini smoke test",
            ):
                self.run_evaluation(
                    str(root / "golden.csv"),
                    str(root / "result.csv"),
                    str(root / "summary.md"),
                    model="gemini-3.5-flash-lite",
                    smoke_test_succeeded=False,
                )

    def test_eval_refuses_to_overwrite_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            golden = root / "golden.csv"
            output = root / "result.csv"
            summary = root / "summary.md"
            golden.write_text("case_id,input\n", encoding="utf-8")
            output.write_text("history", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                self.run_evaluation(
                    str(golden),
                    str(output),
                    str(summary),
                    model="gemini-3.5-flash-lite",
                    smoke_test_succeeded=True,
                )

    def test_eval_writes_all_status_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            golden = root / "golden.csv"
            output = root / "result.csv"
            summary = root / "summary.md"
            fieldnames = [
                "case_id",
                "input",
                "expected_intent",
                "expected_action",
                "risk_class",
                "source_type",
                "source_ref",
                "hard_condition",
                "notes",
            ]
            with golden.open("w", encoding="utf-8", newline="") as target:
                writer = csv.DictWriter(target, fieldnames=fieldnames)
                writer.writeheader()
                for index in range(22):
                    writer.writerow(
                        {
                            "case_id": f"T-{index:02d}",
                            "input": "Xin chào",
                            "expected_intent": "greeting",
                            "expected_action": "answer_briefly",
                            "risk_class": "normal",
                            "source_type": "none",
                            "source_ref": "test",
                            "hard_condition": "FALSE",
                            "notes": "",
                        }
                    )
            result = {
                "intent": "greeting",
                "confidence": 0.9,
                "action": "answer_briefly",
                "is_fallback": False,
                "model_requested": "gemini-3.5-flash-lite",
                "model_used": "gemini-3.5-flash-lite",
                "used_fallback": False,
                "knowledge_id": None,
                "source_ids": [],
                "source_verified": False,
                "error_type": "",
                "error_code": None,
                "reply": "Xin chào.",
                "rationale": "Chào hỏi.",
            }
            config = GeminiConfig(
                api_key="unit-test-key",
                model="gemini-3.5-flash-lite",
                endpoint="https://example.invalid",
                timeout=30,
            )
            with patch("run_eval.get_gemini_config", return_value=config):
                with patch("run_eval.classify_message", return_value=result):
                    summary_result = self.run_evaluation(
                        str(golden),
                        str(output),
                        str(summary),
                        model="gemini-3.5-flash-lite",
                        smoke_test_succeeded=True,
                    )
            with output.open(encoding="utf-8") as source:
                rows = list(csv.DictReader(source))
        self.assertEqual(len(rows), 22)
        self.assertTrue(all(row["status"] == "PASS" for row in rows))
        self.assertEqual(summary_result["pass_count"], 22)


if __name__ == "__main__":
    unittest.main()
