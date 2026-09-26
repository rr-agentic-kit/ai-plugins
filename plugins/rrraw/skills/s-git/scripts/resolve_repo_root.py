#!/usr/bin/env python3
"""Resolve and validate REPO_ROOT in one shot.

  python3 resolve_repo_root.py
  python3 resolve_repo_root.py --candidate <path>

Stdout: key=value. Exit 0 on ok; 1 on error.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _emit(**kwargs: object) -> None:
    for key, value in kwargs.items():
        if value is None:
            continue
        print(f"{key}={value}")


def _fail(error: str, message: str, remediation: str = "") -> int:
    _emit(status="error", error=error, message=message, remediation=remediation or None)
    print(f"error: {message}", file=sys.stderr)
    if remediation:
        print(remediation, file=sys.stderr)
    return 1


def _git_toplevel(cwd: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    top = result.stdout.strip()
    return top or None


def resolve(candidate: Path | None) -> tuple[str | None, str | None, str]:
    """Return (repo_root, error_code, message)."""
    if candidate is None:
        cwd = Path.cwd()
        top = _git_toplevel(cwd)
        if not top:
            return None, "not_repo", "git rev-parse --show-toplevel failed in cwd"
        return top, None, ""

    if not candidate.exists():
        return None, "missing", f"candidate path does not exist: {candidate}"
    if not candidate.is_dir():
        return None, "not_dir", f"candidate is not a directory: {candidate}"

    top = _git_toplevel(candidate)
    if not top:
        return None, "not_repo", f"not a git work tree: {candidate}"

    try:
        abs_candidate = str(candidate.resolve())
    except OSError as exc:
        return None, "resolve_failed", f"could not resolve candidate: {exc}"

    if abs_candidate != top:
        return (
            None,
            "not_root",
            f"pass the repository root, not a subdirectory (got {abs_candidate}; root is {top})",
        )
    return top, None, ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve/validate REPO_ROOT")
    parser.add_argument(
        "--candidate",
        type=Path,
        default=None,
        help="User-supplied path (--repo / -C). Omit to use cwd toplevel.",
    )
    args = parser.parse_args(argv)

    root, err, message = resolve(args.candidate)
    if err:
        remediation = "Pass the clone root, or omit --candidate to use cwd."
        if err == "not_root" and root is None and "root is " in message:
            remediation = message
        return _fail(err, message, remediation)

    _emit(status="ok", repo_root=root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
