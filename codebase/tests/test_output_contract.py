import json
import unittest

from output_contract import validate_model_output


def valid_output(**overrides):
    output = {
        "intent": "learning",
        "confidence": 0.91,
        "action": "answer_with_guidance",
        "reply": "Mình sẽ gợi ý từng bước để bạn tự giải quyết.",
        "rationale": "Đây là câu hỏi học tập.",
    }
    output.update(overrides)
    return json.dumps(output, ensure_ascii=False)


class OutputContractTest(unittest.TestCase):
    def test_valid_json_is_accepted(self):
        result = validate_model_output(valid_output())
        self.assertEqual(result["intent"], "learning")
        self.assertEqual(result["action"], "answer_with_guidance")
        self.assertEqual(result["confidence"], 0.91)

    def test_missing_field_returns_safe_fallback(self):
        payload = json.loads(valid_output())
        del payload["reply"]
        result = validate_model_output(json.dumps(payload))
        self.assertEqual(result["intent"], "ambiguous")
        self.assertEqual(result["action"], "ask_clarifying_question")

    def test_invalid_intent_returns_safe_fallback(self):
        result = validate_model_output(valid_output(intent="other"))
        self.assertEqual(result["intent"], "ambiguous")
        self.assertEqual(result["confidence"], 0.0)

    def test_invalid_confidence_returns_safe_fallback(self):
        for confidence in (-0.01, 1.01, True, "high"):
            with self.subTest(confidence=confidence):
                result = validate_model_output(valid_output(confidence=confidence))
                self.assertEqual(result["action"], "ask_clarifying_question")
                self.assertEqual(result["confidence"], 0.0)

    def test_plain_text_returns_safe_fallback(self):
        result = validate_model_output("Đây không phải JSON.")
        self.assertEqual(result["intent"], "ambiguous")
        self.assertEqual(result["action"], "ask_clarifying_question")

    def test_fabricated_logistics_returns_handoff_without_claim(self):
        result = validate_model_output(
            valid_output(
                intent="logistics",
                confidence=0.95,
                action="handoff_to_ta",
                reply="Deadline là 20/08 và nộp tại https://example.test/nop-bai.",
                rationale="Thông tin lịch nộp bài.",
            )
        )
        self.assertEqual(result["intent"], "logistics")
        self.assertEqual(result["action"], "handoff_to_ta")
        self.assertNotIn("20/08", result["reply"])
        self.assertNotIn("https://", result["reply"])

    def test_invalid_action_returns_safe_fallback(self):
        result = validate_model_output(valid_output(action="invent_an_answer"))
        self.assertEqual(result["intent"], "ambiguous")
        self.assertEqual(result["action"], "ask_clarifying_question")

    def test_out_of_scope_request_is_valid_when_declined(self):
        result = validate_model_output(
            valid_output(
                intent="out_of_scope",
                confidence=0.98,
                action="decline_and_redirect",
                reply=(
                    "Mình không thể làm bài hộ, nhưng có thể giải thích khái niệm "
                    "hoặc góp ý phần bạn đã làm."
                ),
                rationale="Người dùng yêu cầu đáp án hoàn chỉnh.",
            )
        )
        self.assertEqual(result["intent"], "out_of_scope")
        self.assertEqual(result["action"], "decline_and_redirect")

    def test_empty_output_returns_safe_fallback(self):
        for empty_value in (None, "", "   "):
            with self.subTest(empty_value=empty_value):
                result = validate_model_output(empty_value)
                self.assertEqual(result["intent"], "ambiguous")
                self.assertEqual(result["action"], "ask_clarifying_question")

    def test_ungrounded_logistics_must_handoff(self):
        result = validate_model_output(
            valid_output(
                intent="logistics",
                confidence=0.90,
                action="handoff_to_ta",
                reply="Mình chưa có nguồn chính thức; mình sẽ chuyển TA xác nhận.",
                rationale="Không có nguồn logistics đã xác minh.",
            )
        )
        self.assertEqual(result["intent"], "logistics")
        self.assertEqual(result["action"], "handoff_to_ta")

    def test_low_confidence_answer_is_rejected(self):
        result = validate_model_output(valid_output(confidence=0.40))
        self.assertEqual(result["action"], "ask_clarifying_question")
        self.assertEqual(result["confidence"], 0.0)

    def test_verified_logistics_can_use_grounded_details(self):
        result = validate_model_output(
            valid_output(
                intent="logistics",
                confidence=0.93,
                action="answer_briefly",
                reply="Theo nguồn đã xác minh, hạn nộp là 20/08.",
                rationale="Câu trả lời dựa trên nguồn logistics được ứng dụng cung cấp.",
            ),
            has_verified_logistics_source=True,
        )
        self.assertEqual(result["action"], "answer_briefly")
        self.assertEqual(result["confidence"], 0.93)


if __name__ == "__main__":
    unittest.main()
