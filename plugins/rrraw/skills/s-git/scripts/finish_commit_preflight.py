#!/usr/bin/env python3
"""Preflight before finishing a merge/rebase commit.

  python3 finish_commit_preflight.py
  python3 finish_commit_preflight.py --repo <path>
  python3 finish_commit_preflight.py --warn-threshold 50

Stdout: key=value (staged_count, hooks_likely, warn). Exit 0 on ok; 1 on error.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HOOK_MARKERS = (
    ".husky/pre-commit",
    ".lintstagedrc",
    ".lintstagedrc.js",
    ".lintstagedrc.cjs",
    ".lintstagedrc.mjs",
    ".lintstagedrc.json",
    ".lintstagedrc.yaml",
    ".lintstagedrc.yml",
    "lint-staged.config.js",
    "lint-staged.config.cjs",
    "lint-staged.config.mjs",
)


def _emit(**kwargs: object) -> None:
    for key, value in kwargs.items():
        if value is None:
            continue
        if isinstance(value, bool):
            print(f"{key}={'yes' if value else 'no'}")
        else:
            print(f"{key}={value}")


def _fail(error: str, message: str, remediation: str = "") -> int:
    _emit(status="error", error=error, message=message, remediation=remediation or None)
    print(f"error: {message}", file=sys.stderr)
    if remediation:
        print(remediation, file=sys.stderr)
    return 1


def _run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def _staged_count(repo: Path) -> int:
    result = _run_git(repo, "diff", "--cached", "--name-only")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff --cached failed")
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return len(lines)


def _hooks_likely(repo: Path) -> bool:
    for rel in HOOK_MARKERS:
        if (repo / rel).exists():
            return True
    pkg = repo / "package.json"
    if pkg.is_file():
        try:
            text = pkg.read_text(encoding="utf-8")
        except OSError:
            return False
        if '"lint-staged"' in text or "'lint-staged'" in text:
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Finish-commit preflight")
    parser.add_argument(
        "--repo", type=Path, default=None, help="Git repo root (default: cwd)"
    )
    parser.add_argument(
        "--warn-threshold",
        type=int,
        default=50,
        help="Warn when hooks_likely and staged_count >= this (default: 50)",
    )
    args = parser.parse_args(argv)

    repo = (args.repo or Path.cwd()).resolve()
    probe = _run_git(repo, "rev-parse", "--is-inside-work-tree")
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        return _fail(
            "not_repo", f"not a git work tree: {repo}", "Pass --repo <clone-root>."
        )

    try:
        count = _staged_count(repo)
    except RuntimeError as exc:
        return _fail("git_failed", str(exc))

    hooks = _hooks_likely(repo)
    warn = hooks and count >= args.warn_threshold
    _emit(
        status="ok",
        staged_count=count,
        hooks_likely=hooks,
        warn=warn,
        warn_threshold=args.warn_threshold,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
