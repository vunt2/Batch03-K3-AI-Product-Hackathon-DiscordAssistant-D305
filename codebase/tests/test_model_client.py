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
        self.assertIn('"intent": "greeting"', output)
        self.assertEqual(metadata["model_used"], DEFAULT_GEMINI_MODEL)
        self.assertNotIn(GEMINI_KEY, repr(metadata))

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
