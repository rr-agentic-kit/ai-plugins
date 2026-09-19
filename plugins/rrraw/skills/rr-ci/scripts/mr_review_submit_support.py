from __future__ import annotations

import sys
from dataclasses import dataclass

from glab import GlabClient
from mr_review_submit_api import (
    Decision,
    _append_reviewer,
    _fetch_review_context,
    _is_reviewer,
    _my_review_state,
)
from mr_review_submit_decisions import (
    _emit_dry_run,
    _soft_reject,
    _submit_decision,
)


@dataclass(frozen=True)
class ReviewContext:
    resolved_iid: str
    project_path: str
    username: str
    review_state: str | None
    needs_reviewer: bool


def _log_review_context(
    *,
    resolved_iid: str,
    username: str,
    decision: Decision,
    dry_run: bool,
) -> None:
    print(f"MR IID: {resolved_iid}", file=sys.stderr)
    print(f"user: {username}", file=sys.stderr)
    print(f"decision: {decision}", file=sys.stderr)
    if dry_run:
        print("dry-run: no API mutations will be performed", file=sys.stderr)


def _append_reviewer_if_needed(
    client: GlabClient,
    *,
    project_path: str,
    resolved_iid: str,
    username: str,
    needs_reviewer: bool,
) -> tuple[bool, int | None]:
    if not needs_reviewer:
        return False, None

    errors = _append_reviewer(client, project_path, resolved_iid, username)
    if errors:
        return False, _soft_reject(
            "; ".join(errors),
            mr_iid=resolved_iid,
            reviewer_added=False,
        )
    print("reviewer appended", file=sys.stderr)
    return True, None


def build_review_context(
    client: GlabClient,
    *,
    resolved_iid: str,
    project_path: str,
    username: str,
) -> ReviewContext:
    reviewers, _author = _fetch_review_context(client, project_path, resolved_iid)
    already_reviewer = _is_reviewer(reviewers, username)
    return ReviewContext(
        resolved_iid=resolved_iid,
        project_path=project_path,
        username=username,
        review_state=_my_review_state(reviewers, username),
        needs_reviewer=not already_reviewer,
    )


def _submit_after_reviewer(
    client: GlabClient,
    context: ReviewContext,
    *,
    decision: Decision,
    reviewer_added: bool,
) -> int:
    return _submit_decision(
        client,
        project_path=context.project_path,
        mr_iid=context.resolved_iid,
        decision=decision,
        review_state=context.review_state,
        reviewer_added=reviewer_added,
    )


def _handle_live_review(
    client: GlabClient,
    context: ReviewContext,
    *,
    decision: Decision,
) -> int:
    reviewer_added, early = _append_reviewer_if_needed(
        client,
        project_path=context.project_path,
        resolved_iid=context.resolved_iid,
        username=context.username,
        needs_reviewer=context.needs_reviewer,
    )
    if early is not None:
        return early

    return _submit_after_reviewer(
        client,
        context,
        decision=decision,
        reviewer_added=reviewer_added,
    )


def execute_review_submit(
    client: GlabClient,
    *,
    resolved_iid: str,
    project_path: str,
    username: str,
    decision: Decision,
    dry_run: bool,
) -> int:
    context = build_review_context(
        client,
        resolved_iid=resolved_iid,
        project_path=project_path,
        username=username,
    )
    _log_review_context(
        resolved_iid=context.resolved_iid,
        username=context.username,
        decision=decision,
        dry_run=dry_run,
    )
    if dry_run:
        return _emit_dry_run(
            mr_iid=context.resolved_iid,
            decision=decision,
            reviewer_added=context.needs_reviewer,
        )

    return _handle_live_review(client, context, decision=decision)
