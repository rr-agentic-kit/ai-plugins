"""Token budget CLI for rr-planner plan docs (tiktoken, not character guess)."""

from __future__ import annotations

__all__ = ["ENCODING_NAME", "HARD_THRESHOLD", "SOFT_THRESHOLD"]

SOFT_THRESHOLD = 5_000
HARD_THRESHOLD = 8_000
ENCODING_NAME = "cl100k_base"
