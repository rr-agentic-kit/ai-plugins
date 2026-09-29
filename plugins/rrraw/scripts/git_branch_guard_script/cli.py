"""argparse CLI for git_branch_guard --hook."""

from __future__ import annotations

import argparse
import sys


def run_hook_mode(runtime: str) -> int:
    """Read host JSON from stdin; print deny JSON or stay silent. Always exit 0."""
    from .hook import run_hook

    try:
        stdin_text = sys.stdin.read()
    except OSError:
        return 0
    try:
        out = run_hook(runtime=runtime, stdin_text=stdin_text)
    except Exception:
        return 0
    if out:
        sys.stdout.write(out)
        if not out.endswith("\n"):
            sys.stdout.write("\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="git_branch_guard",
        description="Deny branch-mutating git writes on protected branches",
    )
    parser.add_argument(
        "--hook",
        action="store_true",
        required=True,
        help="Dual-runtime hook adapter (stdin = host JSON)",
    )
    parser.add_argument(
        "--runtime",
        choices=("cursor", "claude"),
        required=True,
        help="Emit cursor or claude deny shape",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_hook_mode(args.runtime)
