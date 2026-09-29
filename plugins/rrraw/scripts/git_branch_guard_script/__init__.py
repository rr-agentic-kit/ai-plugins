"""Blocks `git commit` on protected branches (master/main) — dual-runtime hook."""

from __future__ import annotations

__all__ = ["PROTECTED_BRANCHES"]

PROTECTED_BRANCHES = frozenset({"master", "main"})
