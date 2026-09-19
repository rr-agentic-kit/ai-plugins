from __future__ import annotations

import argparse

import emit
from glab import GlabClient, default_glab
from mr_common import auth_check as _auth_check
from mr_common import current_username as _current_username
from mr_common import project_path as _project_path
from mr_common import resolve_mr_iid as _resolve_mr_iid
from mr_review_submit_api import (
    COMMAND,
    Decision,
    Status,
    _append_reviewer,
    _approve,
)
from mr_review_submit_decisions import (
    _emit_decision,
    _emit_dry_run,
    _emit_result,
    _submit_decision,
)
from mr_review_submit_support import execute_review_submit

__all__ = [
    "COMMAND",
    "Decision",
    "Status",
    "_append_reviewer",
    "_approve",
    "_emit_decision",
    "_emit_dry_run",
    "_emit_result",
    "_handler",
    "_submit_decision",
    "add_parser",
    "main",
]


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        COMMAND,
        help="Ensure MR reviewer and submit review decision (request-changes or approve)",
        description=(
            "Result keys: status (requested_changes|approved|reviewer_only|"
            "unchanged|rejected|would-submit), reviewer_added, mr_iid, reason"
        ),
    )
    parser.add_argument("mr_iid", nargs="?", help="Merge request IID")
    parser.add_argument(
        "--decision",
        choices=["request-changes", "approve", "none"],
        default="none",
        help="Review decision to submit (default: none = reviewer only)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print intended actions without API calls"
    )
    parser.set_defaults(handler=_handler)


def _handler(args: argparse.Namespace) -> int:
    return main(
        mr_iid=args.mr_iid,
        decision=args.decision,
        dry_run=args.dry_run,
    )


def _execute_review_submit(
    client: GlabClient,
    *,
    mr_iid: str | None,
    decision: Decision,
    dry_run: bool,
) -> int:
    _auth_check(client)
    resolved_iid = _resolve_mr_iid(client, mr_iid)
    return execute_review_submit(
        client,
        resolved_iid=resolved_iid,
        project_path=_project_path(client),
        username=_current_username(client),
        decision=decision,
        dry_run=dry_run,
    )


def main(
    *,
    mr_iid: str | None = None,
    decision: Decision = "none",
    dry_run: bool = False,
    glab: GlabClient | None = None,
) -> int:
    client = glab or default_glab()
    return emit.run_guarded(
        COMMAND,
        lambda: _execute_review_submit(
            client,
            mr_iid=mr_iid,
            decision=decision,
            dry_run=dry_run,
        ),
    )
