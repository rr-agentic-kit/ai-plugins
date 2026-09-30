"""Fail-closed secret scrubbing for auto-learn scratch + inject."""

from __future__ import annotations

import re

_REDACTED = "[REDACTED]"
_REDACTED_KEEP = rf"\1{_REDACTED}"

# (pattern, replacement). Keep labels; scrub values.
_SECRET_SUBS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)\S+"),
        _REDACTED_KEEP,
    ),
    (re.compile(r"(?i)\b(bearer\s+)\S+"), _REDACTED_KEEP),
    (
        re.compile(
            r"(?i)(\b(?:api[_-]?key|secret|token|password|passwd|access[_-]?token)"
            r"\s*[:=]\s*)([^\s\"']+)"
        ),
        _REDACTED_KEEP,
    ),
    (
        re.compile(r"(?i)(-{1,2}(?:api[_-]?key|token|password|secret)\s+)\S+"),
        _REDACTED_KEEP,
    ),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"), _REDACTED),
    (re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"), _REDACTED),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), _REDACTED),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"), _REDACTED),
)


def redact_secrets(text: str | None) -> str:
    """Replace common secret shapes with [REDACTED]. Empty/None → \"\"."""
    if not text:
        return ""
    out = text
    for pat, repl in _SECRET_SUBS:
        out = pat.sub(repl, out)
    return out
