"""Deterministic removal of common secret material from report text."""

from __future__ import annotations

import re


REDACTED = "[REDACTED]"
_PRIVATE_KEY = re.compile(
    r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----.*?-----END (?:[A-Z ]+ )?PRIVATE KEY-----",
    re.IGNORECASE | re.DOTALL,
)
_BEARER = re.compile(r"(?i)\b(Bearer\s+)[A-Za-z0-9._~+/=-]{8,}")
_KEY_VALUE = re.compile(
    r"(?i)\b(password|passwd|api[_-]?key|access[_-]?token|refresh[_-]?token|secret)"
    r"(\s*[:=]\s*)([^\s,;\"']+)"
)
_COOKIE = re.compile(r"(?im)^(Cookie|Set-Cookie)(\s*:\s*)([^\r\n]+)$")


def redact_text(value: str) -> str:
    text = str(value)
    text = _PRIVATE_KEY.sub(REDACTED, text)
    text = _BEARER.sub(lambda match: match.group(1) + REDACTED, text)
    text = _KEY_VALUE.sub(
        lambda match: match.group(1) + match.group(2) + REDACTED,
        text,
    )
    text = _COOKIE.sub(lambda match: match.group(1) + match.group(2) + REDACTED, text)
    return text


def redact_lines(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(redact_text(value) for value in values)
