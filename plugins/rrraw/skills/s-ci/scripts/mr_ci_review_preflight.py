"""CI review scope preflight (`outcome: ci` only).

Not used for report/fix reviews — those use local `HEAD` and
`scripts/scope/resolve-merge-base.sh` instead. Invoked by the review
orchestrator before assess when publishing MR inline comments (`--ci`).
"""

from __future__ import annotations

import argparse
from typing import Any

import emit
from gitutil import (
    diff_name_only,
    fetch_remote_branches,
    merge_base_refs,
    remote_ref,
    repo_root,
    require_worktree,
)
from glab import GlabClient, default_glab
from mr_common import auth_check as _auth_check
from mr_common import resolve_open_mr as _resolve_open_mr

COMMAND = "mr-ci-review-preflight"
DEFAULT_REMOTE = "origin"


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        COMMAND,
        help=(
            "CI-only review scope preflight (outcome: ci): "
            "resolve open MR, fetch, merge-base, allowlist, read_ref"
        ),
        description=(
            "For review orchestrator outcome: ci only — not report/fix. "
            "Resolves MR branches on origin, builds diff allowlist and READ_REF. "
            "Result keys: mr_iid, source_branch, target_branch, merge_base, "
            "head_ref, read_ref, ref_range, allowlist, scope, diff_refs"
        ),
    )
    parser.add_argument(
        "mr_ref",
        nargs="?",
        help="Optional MR URL, !IID, or numeric IID (omit to auto-discover open MR)",
    )
    parser.set_defaults(handler=_handler)


def _handler(args: argparse.Namespace) -> int:
    return main(mr_ref=args.mr_ref)


def _build_scope(merge_base: str, head_ref: str, repo: str) -> dict[str, Any]:
    del repo
    return {"paths": diff_name_only(merge_base, head_ref)}


def _normalize_mr_labels(labels: list[Any] | None) -> list[str]:
    if not labels:
        return []
    if isinstance(labels[0], dict):
        return [str(item.get("name", "")) for item in labels]
    return [str(label) for label in labels]


def _ci_scope_result(
    mr: dict[str, Any], *, merge_base: str, head_ref: str, repo: str
) -> dict[str, Any]:
    allowlist = diff_name_only(merge_base, head_ref)
    ref_range = f"{merge_base}..{head_ref}"
    label_names = _normalize_mr_labels(mr.get("labels"))
    scope = _build_scope(merge_base, head_ref, repo)

    return {
        "mr_iid": str(mr.get("iid", "")),
        "mr_url": str(mr.get("web_url", "")),
        "mr_title": str(mr.get("title", "")),
        "mr_description": str(mr.get("description") or ""),
        "mr_labels": label_names,
        "source_branch": str(mr.get("source_branch", "")),
        "target_branch": str(mr.get("target_branch", "")),
        "diff_refs": mr.get("diff_refs") or {},
        "merge_base": merge_base,
        "head_ref": head_ref,
        "read_ref": head_ref,
        "ref_range": ref_range,
        "allowlist": allowlist,
        "scope": scope,
    }


def _run_ci_scope_preflight(mr_ref: str | None, glab: GlabClient) -> dict[str, Any]:
    require_worktree()
    _auth_check(glab)
    repo = repo_root()
    mr = _resolve_open_mr(glab, mr_ref)

    source = str(mr["source_branch"])
    target = str(mr["target_branch"])
    fetch_remote_branches(DEFAULT_REMOTE, source, target)

    head_ref = remote_ref(DEFAULT_REMOTE, source)
    target_ref = remote_ref(DEFAULT_REMOTE, target)
    merge_base = merge_base_refs(target_ref, head_ref)

    return _ci_scope_result(mr, merge_base=merge_base, head_ref=head_ref, repo=repo)


def main(*, mr_ref: str | None = None, glab: GlabClient | None = None) -> int:
    def _run() -> int:
        client = glab or default_glab()
        result = _run_ci_scope_preflight(mr_ref, client)
        return emit.succeed(COMMAND, result)

    return emit.run_guarded(COMMAND, _run)
