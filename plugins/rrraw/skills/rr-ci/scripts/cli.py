from __future__ import annotations

import argparse
import sys
from typing import cast

import code_quality_reports
import debug_pipeline
import detect_remote
import github_backend
import mr_add_preflight
import mr_ci_review_preflight
import mr_ensure_review_instructions
import mr_review_submit
import mr_skip_threads
import pending_reviews
import pipeline_security_reports
from emit import fail
from forge import detect


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rr-ci",
        description="Forge-agnostic CI helpers (JSON envelope on stdout).",
    )
    parser.add_argument(
        "--forge",
        choices=["github", "gitlab"],
        help="Override origin detection",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    detect_remote.add_parser(subparsers)
    debug_pipeline.add_parser(subparsers)
    code_quality_reports.add_parser(subparsers)
    pipeline_security_reports.add_parser(subparsers)
    mr_skip_threads.add_parser(subparsers)
    mr_add_preflight.add_parser(subparsers)
    mr_ensure_review_instructions.add_parser(subparsers)
    mr_ci_review_preflight.add_parser(subparsers)
    mr_review_submit.add_parser(subparsers)
    pending_reviews.add_parser(subparsers)
    return parser


def _resolve_forge(args: argparse.Namespace) -> str:
    if args.forge:
        return args.forge
    if args.command == "detect-remote":
        return ""
    return detect().forge


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "detect-remote":
        return cast(int, args.handler(args))
    forge = _resolve_forge(args)
    if forge == "unknown":
        return fail(
            args.command,
            "forge_unknown",
            "could not detect github vs gitlab; pass --forge",
        )
    if forge == "github":
        return github_backend.dispatch(args)
    return cast(int, args.handler(args))


if __name__ == "__main__":
    sys.exit(main())
