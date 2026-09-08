from __future__ import annotations

import argparse

import emit
import mr_add_preflight_support as support
from errors import GitError
from gitutil import current_branch, repo_root
from glab import GlabClient, default_glab


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        support.COMMAND,
        help="Deterministic MR-add preflight: fetch, push, existing-MR query",
        description="Result keys: status, mr_url, message, upstream, staged_hint",
    )
    parser.add_argument("--continue-anyway", action="store_true")
    parser.add_argument("--same-name-push", action="store_true")
    parser.add_argument("--branch-name")
    parser.add_argument("--commit-all", action="store_true")
    parser.add_argument("--commit-staged", action="store_true")
    parser.set_defaults(handler=_handler)


def _handler(args: argparse.Namespace) -> int:
    commit_policy = ""
    if args.commit_all:
        commit_policy = support.COMMIT_POLICY_ALL
    elif args.commit_staged:
        commit_policy = support.COMMIT_POLICY_STAGED
    return main(
        continue_anyway=args.continue_anyway,
        same_name_push=args.same_name_push,
        branch_name=args.branch_name,
        commit_policy=commit_policy,
        glab=None,
    )


def _repo_root_or_fail() -> tuple[str, int | None]:
    try:
        return repo_root(), None
    except GitError as exc:
        return "", emit.fail(
            support.COMMAND,
            "git_error",
            str(exc),
            result=support.emit_result("error", extra={"message": str(exc)}),
        )


def _current_branch_or_fail() -> tuple[str, int | None]:
    try:
        return current_branch(), None
    except GitError as exc:
        return "", emit.fail(
            support.COMMAND,
            "git_error",
            "detached HEAD or no current branch",
            result=support.emit_result("error", extra={"message": str(exc)}),
        )


def _run_preflight_with_client(
    repo: str,
    branch: str,
    *,
    continue_anyway: bool,
    same_name_push: bool,
    branch_name: str | None,
    commit_policy: str,
    glab: GlabClient | None,
) -> int:
    client = glab or default_glab()
    return support.run_preflight(
        repo,
        branch,
        continue_anyway=continue_anyway,
        same_name_push=same_name_push,
        branch_name=branch_name,
        commit_policy=commit_policy,
        client=client,
    )


def _run_mr_add_preflight(
    *,
    continue_anyway: bool,
    same_name_push: bool,
    branch_name: str | None,
    commit_policy: str,
    glab: GlabClient | None,
) -> int:
    repo, early = _repo_root_or_fail()
    if early is not None:
        return early

    branch, early = _current_branch_or_fail()
    if early is not None:
        return early

    return _run_preflight_with_client(
        repo,
        branch,
        continue_anyway=continue_anyway,
        same_name_push=same_name_push,
        branch_name=branch_name,
        commit_policy=commit_policy,
        glab=glab,
    )


def main(
    *,
    continue_anyway: bool = False,
    same_name_push: bool = False,
    branch_name: str | None = None,
    commit_policy: str = "",
    glab: GlabClient | None = None,
) -> int:
    return emit.run_guarded(
        support.COMMAND,
        lambda: _run_mr_add_preflight(
            continue_anyway=continue_anyway,
            same_name_push=same_name_push,
            branch_name=branch_name,
            commit_policy=commit_policy,
            glab=glab,
        ),
    )
