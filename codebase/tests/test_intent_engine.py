import unittest

from intent_engine import classify_message


class IntentEngineTest(unittest.TestCase):
    def test_greeting(self):
        self.assertEqual(classify_message("Xin chào bot")["intent"], "greeting")

    def test_learning_question(self):
        self.assertEqual(
            classify_message("Giải thích giúp mình RAG là gì")["intent"], "learning"
        )

    def test_logistics_is_handed_off(self):
        result = classify_message("Deadline nộp CP2 là khi nào?")
        self.assertEqual(result["intent"], "logistics")
        self.assertEqual(result["action"], "handoff_to_ta")

    def test_ambiguous_question_asks_for_context(self):
        result = classify_message("Cái này làm sao?")
        self.assertEqual(result["intent"], "ambiguous")
        self.assertEqual(result["action"], "ask_clarifying_question")

    def test_out_of_scope_request_is_declined(self):
        result = classify_message("Làm hộ mình toàn bộ bài này")
        self.assertEqual(result["intent"], "out_of_scope")
        self.assertEqual(result["action"], "decline_and_redirect")


if __name__ == "__main__":
    unittest.main()
