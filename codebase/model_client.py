"""LLM Model Client for CP3 AI Intent Classifier.

Supports Google Gemini API and OpenAI Chat Completions API using standard
library urllib.request for zero extra runtime dependencies and robust timeout handling.
"""

from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.request
from typing import Any

DEFAULT_MODEL_NAME = "gemini-1.5-flash"
DEFAULT_TIMEOUT_SECONDS = 10.0


class ModelClientError(Exception):
    """Base exception for model client errors."""


class ModelKeyMissingError(ModelClientError):
    """Raised when no API key is configured in the environment."""


class ModelTimeoutError(ModelClientError):
    """Raised when the model API call times out."""


class ModelResponseError(ModelClientError):
    """Raised when the API returns an HTTP error or invalid payload."""


def get_model_config() -> tuple[str, str]:
    """Retrieve (api_key, model_name) from environment variables safely.

    Checks MODEL_API_KEY, GEMINI_API_KEY, and OPENAI_API_KEY in order.
    """
    api_key = (
        os.getenv("MODEL_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or ""
    ).strip()

    model_name = (
        os.getenv("MODEL_NAME") or os.getenv("GEMINI_MODEL") or DEFAULT_MODEL_NAME
    ).strip()

    return api_key, model_name


def call_model_api(
    system_prompt: str,
    user_message: str,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> str:
    """Execute a real LLM model call and return the raw output string.

    Parameters
    ----------
    system_prompt : str
        The versioned system prompt with serialized verified context.
    user_message : str
        The learner's input message.
    timeout : float
        Timeout in seconds for the network request.

    Returns
    -------
    str
        Raw text response from the LLM (expected to be a JSON string).

    Raises
    ------
    ModelKeyMissingError
        If no API key is provided.
    ModelTimeoutError
        If network request exceeds timeout.
    ModelResponseError
        If the remote service returns an error.
    """
    api_key, model_name = get_model_config()

    if not api_key:
        raise ModelKeyMissingError(
            "MODEL_API_KEY chưa được cấu hình. "
            "Vui lòng tạo file .env từ .env.example và đặt MODEL_API_KEY."
        )

    # Detect provider based on model name or key prefix
    is_gemini = (
        model_name.startswith("gemini")
        or api_key.startswith("AIza")
        or "googleapis.com" in os.getenv("MODEL_BASE_URL", "")
    )

    if is_gemini:
        return _call_gemini_api(api_key, model_name, system_prompt, user_message, timeout)
    return _call_openai_api(api_key, model_name, system_prompt, user_message, timeout)


def _call_gemini_api(
    api_key: str,
    model_name: str,
    system_prompt: str,
    user_message: str,
    timeout: float,
) -> str:
    base_url = os.getenv(
        "MODEL_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta/models",
    ).rstrip("/")
    url = f"{base_url}/{model_name}:generateContent?key={api_key}"

    payload: dict[str, Any] = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_message}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1,
        },
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            resp_data = json.loads(response.read().decode("utf-8"))
            candidates = resp_data.get("candidates", [])
            if not candidates:
                raise ModelResponseError("Gemini API trả về candidates rỗng.")
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts or "text" not in parts[0]:
                raise ModelResponseError("Gemini API trả về content parts rỗng.")
            return parts[0]["text"]
    except socket.timeout as err:
        raise ModelTimeoutError(f"Quá thời gian kết nối tới Gemini API ({timeout}s).") from err
    except urllib.error.HTTPError as err:
        error_msg = err.read().decode("utf-8", errors="ignore")
        raise ModelResponseError(f"Gemini API lỗi HTTP {err.code}: {err.reason}") from err
    except urllib.error.URLError as err:
        if isinstance(err.reason, socket.timeout):
            raise ModelTimeoutError(f"Quá thời gian kết nối API ({timeout}s).") from err
        raise ModelResponseError(f"Lỗi kết nối mạng tới Gemini API: {err.reason}") from err
    except Exception as err:
        if isinstance(err, ModelClientError):
            raise
        raise ModelResponseError(f"Lỗi không xác định khi gọi Gemini API: {err}") from err


def _call_openai_api(
    api_key: str,
    model_name: str,
    system_prompt: str,
    user_message: str,
    timeout: float,
) -> str:
    url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")

    payload: dict[str, Any] = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            resp_data = json.loads(response.read().decode("utf-8"))
            choices = resp_data.get("choices", [])
            if not choices:
                raise ModelResponseError("OpenAI API trả về choices rỗng.")
            content = choices[0].get("message", {}).get("content", "")
            if not content:
                raise ModelResponseError("OpenAI API trả về message content rỗng.")
            return content
    except socket.timeout as err:
        raise ModelTimeoutError(f"Quá thời gian kết nối tới OpenAI API ({timeout}s).") from err
    except urllib.error.HTTPError as err:
        raise ModelResponseError(f"OpenAI API lỗi HTTP {err.code}: {err.reason}") from err
    except urllib.error.URLError as err:
        if isinstance(err.reason, socket.timeout):
            raise ModelTimeoutError(f"Quá thời gian kết nối API ({timeout}s).") from err
        raise ModelResponseError(f"Lỗi kết nối mạng tới OpenAI API: {err.reason}") from err
    except Exception as err:
        if isinstance(err, ModelClientError):
            raise
        raise ModelResponseError(f"Lỗi không xác định khi gọi OpenAI API: {err}") from err
