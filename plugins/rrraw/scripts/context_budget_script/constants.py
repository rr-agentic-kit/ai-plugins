"""Constants and path predicates for plan-doc budget walks."""

from __future__ import annotations

from pathlib import Path

from . import HARD_THRESHOLD, SOFT_THRESHOLD

LINK_EXTS = frozenset({".md", ".yaml", ".yml"})


def is_plan_markdown(path: Path) -> bool:
    """True when path looks like a Plan doc under docs/rr/.../plan/."""
    if path.suffix.lower() != ".md":
        return False
    normalized = path.as_posix().replace("\\", "/")
    lower = normalized.lower()
    return "/docs/rr/" in lower and "/plan/" in lower


def tier_for(tokens: int) -> str:
    if tokens >= HARD_THRESHOLD:
        return "hard"
    if tokens >= SOFT_THRESHOLD:
        return "soft"
    return "ok"
