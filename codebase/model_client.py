"""Gemini-only model client for the learner assistant."""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from conversation_context import (
    prepare_conversation_history,
    prepare_current_message,
)
from dotenv import load_dotenv


CODEBASE_DIR = Path(__file__).resolve().parent
ENV_PATH = CODEBASE_DIR / ".env"
load_dotenv(ENV_PATH, override=ENV_PATH.exists())

DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"
DEFAULT_GEMINI_BASE_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
)
DEFAULT_TIMEOUT_SECONDS = 30.0


class ModelClientError(Exception):
    """Base exception carrying display-safe diagnostics only."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_type: str = "model_client_error",
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_type = error_type
        self.safe_message = message


class ModelKeyMissingError(ModelClientError):
    """Raised before networking when GEMINI_API_KEY is empty."""


class ModelTimeoutError(ModelClientError):
    """Raised when Gemini exceeds the configured timeout."""


class ModelResponseError(ModelClientError):
    """Raised when Gemini returns an HTTP error or invalid payload."""


class ModelRateLimitError(ModelResponseError):
    """Raised for Gemini quota or rate-limit responses."""


class ModelConfigError(ModelClientError):
    """Raised when Gemini configuration is invalid."""


@dataclass(frozen=True)
class GeminiConfig:
    """Gemini configuration resolved once for a request."""

    api_key: str
    model: str
    endpoint: str
    timeout: float

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def public_metadata(self, model_used: str | None = None) -> dict[str, object]:
        return {
            "model_requested": self.model,
            "model_used": model_used or self.model,
            "used_fallback": False,
        }


def _first_nonempty(*values: str | None) -> str:
    for value in values:
        if value and value.strip():
            return value.strip()
    return ""


def _validate_timeout(value: str) -> float:
    try:
        timeout = float(value)
    except ValueError as error:
        raise ModelConfigError(
            "GEMINI_TIMEOUT_SECONDS phải là số dương.",
            error_type="configuration_error",
        ) from error
    if not math.isfinite(timeout) or timeout <= 0:
        raise ModelConfigError(
            "GEMINI_TIMEOUT_SECONDS phải là số dương.",
            error_type="configuration_error",
        )
    return timeout


def get_gemini_config() -> GeminiConfig:
    """Read Gemini configuration after the local .env has overridden stale env."""

    return GeminiConfig(
        api_key=_first_nonempty(os.getenv("GEMINI_API_KEY")),
        model=_first_nonempty(
            os.getenv("GEMINI_MODEL"),
            DEFAULT_GEMINI_MODEL,
        ),
        endpoint=DEFAULT_GEMINI_BASE_URL,
        timeout=_validate_timeout(
            _first_nonempty(
                os.getenv("GEMINI_TIMEOUT_SECONDS"),
                str(DEFAULT_TIMEOUT_SECONDS),
            )
        ),
    )


def get_gemini_status() -> dict[str, object]:
    """Return safe status for the UI without exposing credentials."""

    try:
        config = get_gemini_config()
    except ModelConfigError:
        return {
            "configured": False,
            "model": _first_nonempty(
                os.getenv("GEMINI_MODEL"),
                DEFAULT_GEMINI_MODEL,
            ),
        }
    return {
        "configured": config.is_configured,
        "model": config.model,
    }


def call_gemini_api(
    system_prompt: str,
    user_message: str,
    *,
    conversation_history: list[dict[str, str]] | None = None,
    config: GeminiConfig | None = None,
    metadata_out: dict[str, object] | None = None,
) -> str:
    """Call Gemini GenerateContent and return raw text for shared validation."""

    resolved = config or get_gemini_config()
    if metadata_out is not None:
        metadata_out.clear()
        metadata_out.update(resolved.public_metadata())
    if not resolved.is_configured:
        raise ModelKeyMissingError(
            "Chưa cấu hình Gemini API key.",
            error_type="missing_api_key",
        )

    model_path = urllib.parse.quote(resolved.model, safe="-._")
    url = f"{resolved.endpoint}/{model_path}:generateContent"

    safe_user_message = prepare_current_message(user_message)
    safe_history = (
        prepare_conversation_history(conversation_history)
        if conversation_history
        else None
    )

    contents_payload: list[dict[str, Any]] = []
    if safe_history:
        for turn in safe_history:
            role = "model" if turn.get("role") == "assistant" else "user"
            contents_payload.append(
                {
                    "role": role,
                    "parts": [{"text": str(turn.get("content", ""))}],
                }
            )
    contents_payload.append(
        {
            "role": "user",
            "parts": [{"text": safe_user_message}],
        }
    )

    payload: dict[str, Any] = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": contents_payload,
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2,
        },
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": resolved.api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=resolved.timeout,
        ) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except socket.timeout as error:
        raise ModelTimeoutError(
            "Gemini phản hồi quá thời gian cho phép.",
            error_type="timeout",
        ) from error
    except urllib.error.HTTPError as error:
        _raise_http_error(error)
    except urllib.error.URLError as error:
        if isinstance(error.reason, socket.timeout):
            raise ModelTimeoutError(
                "Gemini phản hồi quá thời gian cho phép.",
                error_type="timeout",
            ) from error
        raise ModelResponseError(
            "Không thể kết nối tới Gemini.",
            error_type="network_error",
        ) from error
    except (json.JSONDecodeError, UnicodeError) as error:
        raise ModelResponseError(
            "Gemini trả về dữ liệu không hợp lệ.",
            error_type="invalid_response",
        ) from error

    try:
        candidates = response_data["candidates"]
        parts = candidates[0]["content"]["parts"]
        content = str(parts[0]["text"]).strip()
        if not content:
            raise ValueError("empty content")
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise ModelResponseError(
            "Gemini không trả về nội dung có thể xử lý.",
            error_type="invalid_response",
        ) from error

    model_used = str(response_data.get("modelVersion") or resolved.model)
    if metadata_out is not None:
        metadata_out.clear()
        metadata_out.update(resolved.public_metadata(model_used))
    return content


def _raise_http_error(error: urllib.error.HTTPError) -> None:
    if error.code == 429:
        raise ModelRateLimitError(
            "Gemini đang giới hạn lượt gọi. Vui lòng thử lại sau.",
            status_code=429,
            error_type="rate_limit",
        ) from error
    raise ModelResponseError(
        f"Gemini tạm thời không phản hồi (HTTP {error.code}).",
        status_code=error.code,
        error_type="http_error",
    ) from error
