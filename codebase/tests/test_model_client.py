import json
import os
import socket
import urllib.error
import unittest
from unittest.mock import patch

import _bootstrap  # noqa: F401

from model_client import (
    DEFAULT_GEMINI_MODEL,
    ModelKeyMissingError,
    ModelResponseError,
    ModelTimeoutError,
    call_gemini_api,
    get_gemini_config,
    get_gemini_status,
)


GEMINI_KEY = "unit-test-gemini-key"


class _Response:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self) -> bytes:
        return self.body


def gemini_response() -> bytes:
    return json.dumps(
        {
            "modelVersion": DEFAULT_GEMINI_MODEL,
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps(
                                    {
                                        "intent": "greeting",
                                        "confidence": 0.95,
                                        "action": "answer_briefly",
                                        "reply": "Xin chào.",
                                        "rationale": "Chào hỏi.",
                                    }
                                )
                            }
                        ]
                    }
                }
            ],
        }
    ).encode("utf-8")


class GeminiClientTest(unittest.TestCase):
    def test_defaults_and_safe_status(self):
        with patch.dict(os.environ, {}, clear=True):
            config = get_gemini_config()
            status = get_gemini_status()
        self.assertEqual(config.model, DEFAULT_GEMINI_MODEL)
        self.assertFalse(config.is_configured)
        self.assertFalse(status["configured"])
        self.assertNotIn("api_key", status)

    def test_missing_key_does_not_call_network(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("model_client.urllib.request.urlopen") as urlopen:
                with self.assertRaises(ModelKeyMissingError):
                    call_gemini_api("system", "user")
                urlopen.assert_not_called()

    def test_success_uses_gemini_json_mode_and_safe_metadata(self):
        env = {
            "GEMINI_API_KEY": GEMINI_KEY,
            "GEMINI_MODEL": DEFAULT_GEMINI_MODEL,
            "GEMINI_TIMEOUT_SECONDS": "30",
        }
        with patch.dict(os.environ, env, clear=True):
            with patch(
                "model_client.urllib.request.urlopen",
                return_value=_Response(gemini_response()),
            ) as urlopen:
                metadata = {}
                output = call_gemini_api(
                    "system",
                    "user",
                    metadata_out=metadata,
                )
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertIn(DEFAULT_GEMINI_MODEL, request.full_url)
        self.assertEqual(
            payload["generationConfig"]["responseMimeType"],
            "application/json",
        )
        self.assertLessEqual(payload["generationConfig"]["temperature"], 0.2)
        self.assertEqual(payload["generationConfig"]["temperature"], 0.2)
        self.assertIn('"intent": "greeting"', output)
        self.assertEqual(metadata["model_used"], DEFAULT_GEMINI_MODEL)
        self.assertNotIn(GEMINI_KEY, repr(metadata))

    def test_conversation_history_payload_structure(self):
        env = {
            "GEMINI_API_KEY": GEMINI_KEY,
            "GEMINI_MODEL": DEFAULT_GEMINI_MODEL,
            "GEMINI_TIMEOUT_SECONDS": "30",
        }
        history = [
            {"role": "user", "content": "Hỏi về session_state"},
            {"role": "assistant", "content": "Session state lưu dữ liệu"},
        ]
        with patch.dict(os.environ, env, clear=True):
            with patch(
                "model_client.urllib.request.urlopen",
                return_value=_Response(gemini_response()),
            ) as urlopen:
                call_gemini_api(
                    "system_prompt_text",
                    "Cho mình ví dụ",
                    conversation_history=history,
                )
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        contents = payload["contents"]
        self.assertEqual(len(contents), 3)
        self.assertEqual(contents[0]["role"], "user")
        self.assertEqual(contents[0]["parts"][0]["text"], "Hỏi về session_state")
        self.assertEqual(contents[1]["role"], "model")
        self.assertEqual(contents[1]["parts"][0]["text"], "Session state lưu dữ liệu")
        self.assertEqual(contents[2]["role"], "user")
        self.assertEqual(contents[2]["parts"][0]["text"], "Cho mình ví dụ")
        self.assertEqual(payload["system_instruction"]["parts"][0]["text"], "system_prompt_text")

    def test_direct_model_client_call_redacts_secrets_in_user_message_and_history(self):
        env = {
            "GEMINI_API_KEY": GEMINI_KEY,
            "GEMINI_MODEL": DEFAULT_GEMINI_MODEL,
            "GEMINI_TIMEOUT_SECONDS": "30",
        }
        secret_api_key = "AIza" + "D" * 24
        secret_password = "password=SuperSecret123"
        secret_bearer = "Bearer Token_Secret_XYZ_99999"

        user_input_msg = f"Tôi lỡ gửi key {secret_api_key} và {secret_password}"
        history_input = [
            {"role": "user", "content": f"Trước đó tôi gửi {secret_bearer}"},
            {"role": "assistant", "content": "Tôi đã ghi nhận."},
        ]

        with patch.dict(os.environ, env, clear=True):
            with patch(
                "model_client.urllib.request.urlopen",
                return_value=_Response(gemini_response()),
            ) as urlopen:
                call_gemini_api(
                    "system_prompt",
                    user_input_msg,
                    conversation_history=history_input,
                )

        self.assertEqual(urlopen.call_count, 1)
        request = urlopen.call_args.args[0]
        request_body = request.data.decode("utf-8")

        # Verify raw secrets are completely absent from network payload
        self.assertNotIn(secret_api_key, request_body)
        self.assertNotIn("SuperSecret123", request_body)
        self.assertNotIn("Token_Secret_XYZ_99999", request_body)
        self.assertIn("[REDACTED]", request_body)

        # Verify caller input objects were not mutated
        self.assertIn(secret_api_key, user_input_msg)
        self.assertIn(secret_bearer, history_input[0]["content"])

    def test_timeout_is_sanitized(self):
        env = {"GEMINI_API_KEY": GEMINI_KEY}
        with patch.dict(os.environ, env, clear=True):
            with patch(
                "model_client.urllib.request.urlopen",
                side_effect=socket.timeout(),
            ):
                with self.assertRaises(ModelTimeoutError) as caught:
                    call_gemini_api("system", "user")
        self.assertNotIn(GEMINI_KEY, str(caught.exception))

    def test_http_error_is_sanitized(self):
        error = urllib.error.HTTPError(
            "https://gemini.invalid",
            400,
            f"bad request {GEMINI_KEY}",
            None,
            None,
        )
        with patch.dict(
            os.environ,
            {"GEMINI_API_KEY": GEMINI_KEY},
            clear=True,
        ):
            with patch(
                "model_client.urllib.request.urlopen",
                side_effect=error,
            ):
                with self.assertRaises(ModelResponseError) as caught:
                    call_gemini_api("system", "user")
        self.assertEqual(caught.exception.status_code, 400)
        self.assertNotIn(GEMINI_KEY, str(caught.exception))

    def test_invalid_json_response_fails_safe(self):
        with patch.dict(
            os.environ,
            {"GEMINI_API_KEY": GEMINI_KEY},
            clear=True,
        ):
            with patch(
                "model_client.urllib.request.urlopen",
                return_value=_Response(b"not-json"),
            ):
                with self.assertRaises(ModelResponseError):
                    call_gemini_api("system", "user")


if __name__ == "__main__":
    unittest.main()
