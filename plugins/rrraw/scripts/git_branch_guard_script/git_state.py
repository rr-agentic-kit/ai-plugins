"""Resolves the current git branch for a working directory."""

from __future__ import annotations

import subprocess  # nosec
from pathlib import Path

from . import PROTECTED_BRANCHES


def resolve_branch(cwd: Path) -> str | None:
    """Current branch name at cwd, or None on any infra error (fail-open)."""
    try:
        # Fixed argv list, no shell=True, no untrusted interpolation.
        result = subprocess.run(  # nosec
            ["git", "-C", str(cwd), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except OSError, subprocess.TimeoutExpired:
        return None
    if result.returncode != 0:
        return None
    branch = result.stdout.strip()
    return branch or None


def is_protected_branch(branch: str) -> bool:
    return branch in PROTECTED_BRANCHES
