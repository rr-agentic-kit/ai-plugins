"""argparse CLI for context_budget --file / --plan-dir / --hook."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .constants import is_plan_markdown, tier_for
from .tokenize import count_tokens
from .walk import collect_plan_and_linked


def require_python() -> None:
    if sys.version_info < (3, 14):  # noqa: UP036
        print(
            "context_budget: need CPython 3.14+ with tiktoken "
            "(uv sync --all-groups from monorepo root)",
            file=sys.stderr,
        )
        raise SystemExit(127)


def _report_file(path: Path) -> dict[str, Any] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"context_budget: cannot read {path}: {exc}", file=sys.stderr)
        return None
    tokens = count_tokens(text)
    return {
        "path": str(path.resolve()),
        "tokens": tokens,
        "tier": tier_for(tokens),
    }


def measure_file(path: Path) -> list[dict[str, Any]] | None:
    """In-process file measure. None = not a file / unreadable (CLI exit 2)."""
    if not path.is_file():
        return None
    if not is_plan_markdown(path) and path.suffix.lower() != ".md":
        return []
    report = _report_file(path)
    if report is None:
        return None
    return [report]


def measure_plan_dir(plan_dir: Path) -> list[dict[str, Any]] | None:
    """In-process plan-dir measure. None = not a directory (CLI exit 2)."""
    if not plan_dir.is_dir():
        return None
    reports: list[dict[str, Any]] = []
    for path in collect_plan_and_linked(plan_dir):
        if path.suffix.lower() != ".md":
            continue
        report = _report_file(path)
        if report is not None:
            reports.append(report)
    return reports


def _emit(reports: list[dict[str, Any]]) -> int:
    payload = {"files": reports}
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if any(r["tier"] == "hard" for r in reports):
        return 1
    return 0


def run_file(path: Path) -> int:
    if not path.is_file():
        print(f"context_budget: not a file: {path}", file=sys.stderr)
        return 2
    reports = measure_file(path)
    if reports is None:
        return 2
    return _emit(reports)


def run_plan_dir(plan_dir: Path) -> int:
    if not plan_dir.is_dir():
        print(f"context_budget: not a directory: {plan_dir}", file=sys.stderr)
        return 2
    reports = measure_plan_dir(plan_dir)
    if reports is None:
        return 2
    return _emit(reports)


def run_hook_mode(runtime: str) -> int:
    """Read host JSON from stdin; print inject JSON or stay silent. Always exit 0."""
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
        prog="context_budget",
        description="tiktoken token tiers for rr-planner plan docs",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--file",
        type=Path,
        metavar="PATH",
        help="Measure a single markdown path",
    )
    group.add_argument(
        "--plan-dir",
        type=Path,
        metavar="DIR",
        help="Audit all plan markdown + linked docs under DIR",
    )
    group.add_argument(
        "--hook",
        action="store_true",
        help="Dual-runtime hook adapter (stdin = host JSON)",
    )
    parser.add_argument(
        "--runtime",
        choices=("cursor", "claude"),
        help="Required with --hook: emit cursor or claude inject shape",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    require_python()
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.hook:
        if args.runtime is None:
            parser.error("--hook requires --runtime cursor|claude")
        return run_hook_mode(args.runtime)
    if args.file is not None:
        return run_file(args.file.resolve())
    return run_plan_dir(args.plan_dir.resolve())
