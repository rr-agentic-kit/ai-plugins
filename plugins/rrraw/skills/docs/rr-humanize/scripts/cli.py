from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import cast

import apply_safe
import emit
import scan
import suggest_register


def _read_input(path: str | None) -> str:
    if path and path != "-":
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def _add_input_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="File path or omit for stdin",
    )


def _cmd_scan(args: argparse.Namespace) -> int:
    text = _read_input(args.path)
    if not text.strip():
        return emit.fail("scan", "empty_input", "no text to scan")
    return emit.succeed("scan", scan.scan_text(text))


def _cmd_apply_safe(args: argparse.Namespace) -> int:
    text = _read_input(args.path)
    if not text.strip():
        return emit.fail("apply-safe", "empty_input", "no text to transform")
    return emit.succeed(
        "apply-safe",
        apply_safe.apply_safe_text(text, dry_run=args.dry_run),
    )


def _cmd_suggest_register(args: argparse.Namespace) -> int:
    text = _read_input(args.path)
    if not text.strip():
        return emit.fail("suggest-register", "empty_input", "no text to analyze")
    return emit.succeed("suggest-register", suggest_register.suggest_register_text(text))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="humanize",
        description="Humanize helper CLI (JSON envelope on stdout).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Detect AI-tell patterns")
    _add_input_arg(scan_parser)
    scan_parser.set_defaults(handler=_cmd_scan)

    apply_parser = subparsers.add_parser("apply-safe", help="Apply auto-fixable replacements")
    _add_input_arg(apply_parser)
    apply_parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    apply_parser.set_defaults(handler=_cmd_apply_safe)

    suggest_parser = subparsers.add_parser(
        "suggest-register", help="Heuristic voice/tone from text"
    )
    _add_input_arg(suggest_parser)
    suggest_parser.set_defaults(handler=_cmd_suggest_register)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return cast(int, args.handler(args))


if __name__ == "__main__":
    sys.exit(main())
