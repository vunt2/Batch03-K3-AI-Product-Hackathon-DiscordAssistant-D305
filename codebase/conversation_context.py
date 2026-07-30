"""Helper functions for normalizing and sanitizing conversation context."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from output_contract import redact_sensitive_text


MAX_HISTORY_MESSAGES = 6
MAX_TOTAL_CHARS = 4000
MAX_MESSAGE_CHARS = 1000
MAX_CURRENT_MESSAGE_CHARS = 4000


def prepare_current_message(message: str | None) -> str:
    """Sanitize and truncate copy of user message sent to Gemini.

    - Returns empty string if input is None or not string.
    - Strips whitespace.
    - Redacts secrets (API keys, passwords, bearer tokens, etc.).
    - Caps copy sent to model at MAX_CURRENT_MESSAGE_CHARS.
    - Does not mutate original string.
    """
    if not isinstance(message, str):
        return ""

    clean = message.strip()
    if not clean:
        return ""

    redacted = redact_sensitive_text(clean)
    if len(redacted) > MAX_CURRENT_MESSAGE_CHARS:
        redacted = redacted[:MAX_CURRENT_MESSAGE_CHARS]

    return redacted


def prepare_conversation_history(
    messages: list[Mapping[str, Any]] | None,
) -> list[dict[str, str]]:
    """Normalize session messages into a clean, safe role/content list for Gemini.

    - Excludes internal metadata and welcome messages.
    - Limits to last MAX_HISTORY_MESSAGES messages.
    - Limits total length to MAX_TOTAL_CHARS, per message to MAX_MESSAGE_CHARS.
    - Ensures alternating roles starting with 'user'.
    - Redacts secrets from message content.
    - Does not mutate input list.
    """
    if not messages:
        return []

    cleaned: list[dict[str, str]] = []
    for msg in messages:
        if not isinstance(msg, Mapping):
            continue

        role = msg.get("role")
        content = msg.get("content")

        if not isinstance(role, str) or not isinstance(content, str):
            continue

        role_str = role.strip()
        content_str = content.strip()

        if role_str not in ("user", "assistant") or not content_str:
            continue

        # Skip default welcome message
        if (
            role_str == "assistant"
            and "Chào bạn! Mình có thể tìm câu trả lời" in content_str
        ):
            continue

        # Truncate per-message content length
        if len(content_str) > MAX_MESSAGE_CHARS:
            content_str = content_str[:MAX_MESSAGE_CHARS]

        # Redact secrets
        redacted_content = redact_sensitive_text(content_str)

        cleaned.append({"role": role_str, "content": redacted_content})

    # Take at most last MAX_HISTORY_MESSAGES
    if len(cleaned) > MAX_HISTORY_MESSAGES:
        cleaned = cleaned[-MAX_HISTORY_MESSAGES:]

    # Enforce total character budget (from newest to oldest)
    budget = MAX_TOTAL_CHARS
    budget_fitted: list[dict[str, str]] = []
    for item in reversed(cleaned):
        item_len = len(item["content"])
        if budget >= item_len:
            budget_fitted.append(dict(item))
            budget -= item_len
        elif budget > 0:
            budget_fitted.append(
                {"role": item["role"], "content": item["content"][:budget]}
            )
            budget = 0
            break
        else:
            break
    cleaned = list(reversed(budget_fitted))

    # Ensure history starts with 'user'
    while cleaned and cleaned[0]["role"] != "user":
        cleaned.pop(0)

    if not cleaned:
        return []

    # Enforce strict alternating roles (user -> assistant -> user -> assistant ...)
    alternating: list[dict[str, str]] = []
    for item in cleaned:
        if not alternating:
            if item["role"] == "user":
                alternating.append(item)
        else:
            if item["role"] != alternating[-1]["role"]:
                alternating.append(item)
            else:
                # Replace previous with newest if same role consecutive
                alternating[-1] = item

    return alternating
