from __future__ import annotations

import emit
from emit import omit_empty
from gitutil import (
    DEFAULT_LOCAL_BRANCHES,
    already_merged,
    git_output,
    has_uncommitted_changes,
    opened_mrs_for_branch,
    resolve_integration_base,
    run_git,
    staged_hint,
    upstream_abbrev_ref,
)
from glab import GlabClient

COMMAND = "mr-add-preflight"
COMMIT_POLICY_ALL = "all"
COMMIT_POLICY_STAGED = "staged"


def emit_result(status: str, *, extra: dict[str, str] | None = None) -> dict[str, str]:
    result: dict[str, str] = {"status": status}
    if extra:
        result.update(extra)
    return omit_empty(result)


def _emit_needs_branch_from_default() -> int:
    hint = staged_hint()
    return emit.succeed(
        COMMAND,
        emit_result(
            "needs_branch_from_default",
            extra={
                "staged_hint": hint,
                "message": (
                    "on default branch with uncommitted changes; "
                    "provide --branch-name and commit policy"
                ),
            },
        ),
    )


def _snapshot_commit_push(
    _repo: str,
    branch_name: str,
    commit_policy: str,
) -> tuple[str, int | None]:
    run_git(["checkout", "-b", branch_name])
    if commit_policy == COMMIT_POLICY_ALL:
        run_git(["add", "."])
        run_git(["commit", "-m", "chore: snapshot uncommitted work"])
    else:
        run_git(["commit", "-m", "chore: snapshot staged work"])

    push = run_git(["push", "-u", "origin", branch_name], check=False)
    if push.returncode != 0:
        return branch_name, emit.fail(
            COMMAND,
            "push_failed",
            f"push failed for branch {branch_name}",
            result=emit_result(
                "error",
                extra={"message": f"push failed for branch {branch_name}"},
            ),
        )
    return branch_name, None


def handle_default_branch_snapshot(
    _repo: str,
    branch: str,
    *,
    branch_name: str | None,
    commit_policy: str,
) -> tuple[str, int | None]:
    if branch not in DEFAULT_LOCAL_BRANCHES or not has_uncommitted_changes():
        return branch, None

    if not branch_name:
        return branch, _emit_needs_branch_from_default()

    if commit_policy not in (COMMIT_POLICY_ALL, COMMIT_POLICY_STAGED):
        return branch, emit.fail(
            COMMAND,
            "usage_error",
            "--branch-name requires --commit-all or --commit-staged",
        )

    return _snapshot_commit_push(_repo, branch_name, commit_policy)


def _upstream_escalation(branch: str, upstream: str) -> int:
    message = f"upstream {upstream} != origin/{branch}; use --same-name-push or abort"
    return emit.succeed(
        COMMAND,
        emit_result(
            "escalate_upstream",
            extra={"upstream": upstream, "message": message},
        ),
    )


def _check_upstream_mismatch(
    branch: str,
    *,
    same_name_push: bool,
) -> int | None:
    upstream = upstream_abbrev_ref()
    if upstream is None:
        return None

    upstream_short = upstream.removeprefix("origin/")
    if upstream_short == branch or same_name_push:
        return None

    return _upstream_escalation(branch, upstream)


def _needs_push(branch: str, *, same_name_push: bool) -> bool:
    if same_name_push:
        return True

    upstream = upstream_abbrev_ref()
    if upstream is None:
        return True

    remote_ref = f"origin/{branch}"
    return (
        run_git(["rev-parse", "--verify", "-q", remote_ref], check=False).returncode
        != 0
    )


def _push_branch(branch: str) -> int | None:
    push = run_git(["push", "-u", "origin", f"HEAD:refs/heads/{branch}"], check=False)
    if push.returncode == 0:
        return None

    return emit.fail(
        COMMAND,
        "push_failed",
        f"push failed for origin/{branch}",
        result=emit_result(
            "error",
            extra={"message": f"push failed for origin/{branch}"},
        ),
    )


def _lookup_open_mr_url(client: GlabClient, branch: str) -> str:
    mrs = opened_mrs_for_branch(client, branch)
    if mrs:
        return str(mrs[0].get("web_url", ""))
    return ""


def _has_commits_to_merge(base: str) -> bool:
    range_count = git_output(["rev-list", "--count", f"{base}..HEAD"])
    return int(range_count) > 0


def _merged_escalation(
    base: str,
    *,
    continue_anyway: bool,
) -> int | None:
    if continue_anyway:
        return None

    merged, _evidence = already_merged(base)
    if not merged:
        return None

    message = f"commits look already in {base}; abort (default) or --continue-anyway"
    return emit.succeed(
        COMMAND,
        emit_result("escalate_merged", extra={"message": message}),
    )


def _mr_lookup_result(branch: str, client: GlabClient) -> int:
    mr_url = _lookup_open_mr_url(client, branch)
    if mr_url:
        return emit.succeed(
            COMMAND,
            emit_result(
                "exists",
                extra={"mr_url": mr_url, "message": "MR already exists"},
            ),
        )

    return emit.succeed(
        COMMAND,
        emit_result("ready_create", extra={"message": "ready to create draft MR"}),
    )


def _push_and_lookup_mr(
    branch: str,
    base: str,
    client: GlabClient,
    *,
    same_name_push: bool,
) -> int:
    if _needs_push(branch, same_name_push=same_name_push):
        early = _push_branch(branch)
        if early is not None:
            return early

    if not _has_commits_to_merge(base):
        return emit.fail(
            COMMAND,
            "no_commits",
            "No commits to merge",
            result=emit_result("no_commits", extra={"message": "No commits to merge"}),
        )

    return _mr_lookup_result(branch, client)


def _run_preflight_gates(
    branch: str,
    base: str,
    *,
    continue_anyway: bool,
    same_name_push: bool,
) -> int | None:
    early = _merged_escalation(base, continue_anyway=continue_anyway)
    if early is not None:
        return early

    return _check_upstream_mismatch(branch, same_name_push=same_name_push)


def _run_after_snapshot(
    branch: str,
    client: GlabClient,
    *,
    continue_anyway: bool,
    same_name_push: bool,
) -> int:
    base = resolve_integration_base()

    early = _run_preflight_gates(
        branch,
        base,
        continue_anyway=continue_anyway,
        same_name_push=same_name_push,
    )
    if early is not None:
        return early

    return _push_and_lookup_mr(
        branch,
        base,
        client,
        same_name_push=same_name_push,
    )


def run_preflight(
    _repo: str,
    branch: str,
    *,
    continue_anyway: bool,
    same_name_push: bool,
    branch_name: str | None,
    commit_policy: str,
    client: GlabClient,
) -> int:
    branch, early = handle_default_branch_snapshot(
        _repo,
        branch,
        branch_name=branch_name,
        commit_policy=commit_policy,
    )
    if early is not None:
        return early

    return _run_after_snapshot(
        branch,
        client,
        continue_anyway=continue_anyway,
        same_name_push=same_name_push,
    )
