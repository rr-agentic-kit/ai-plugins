from __future__ import annotations

import sys
from typing import Any

import emit
from glab import GlabClient
from mr_review_submit_api import (
    COMMAND,
    Decision,
    Status,
    _approve,
    _request_changes,
)

__all__ = [
    "_emit_decision",
    "_emit_dry_run",
    "_emit_result",
    "_soft_reject",
    "_submit_decision",
]


def _emit_result(
    status: Status,
    *,
    mr_iid: str,
    reviewer_added: bool,
    **extra: Any,
) -> int:
    payload: dict[str, Any] = {
        "status": status,
        "mr_iid": mr_iid,
        "reviewer_added": reviewer_added,
    }
    payload.update(extra)
    return emit.succeed(COMMAND, payload)


def _soft_reject(reason: str, *, mr_iid: str, reviewer_added: bool) -> int:
    print(f"rejected: {reason}", file=sys.stderr)
    return _emit_result(
        "rejected",
        mr_iid=mr_iid,
        reviewer_added=reviewer_added,
        reason=reason,
    )


def _emit_dry_run(
    *,
    mr_iid: str,
    decision: Decision,
    reviewer_added: bool,
) -> int:
    print(
        f"dry-run: would submit decision={decision} on MR !{mr_iid}",
        file=sys.stderr,
    )
    if reviewer_added:
        print("dry-run: would append current user as reviewer", file=sys.stderr)
    return _emit_result(
        "would-submit",
        mr_iid=mr_iid,
        reviewer_added=reviewer_added,
        decision=decision,
    )


def _emit_unchanged(mr_iid: str, reviewer_added: bool, label: str) -> int:
    print(f"unchanged: already {label}", file=sys.stderr)
    return _emit_result("unchanged", mr_iid=mr_iid, reviewer_added=reviewer_added)


def _emit_decision(
    status: Status,
    *,
    mr_iid: str,
    reviewer_added: bool,
    message: str,
) -> int:
    print(message, file=sys.stderr)
    return _emit_result(status, mr_iid=mr_iid, reviewer_added=reviewer_added)


def _submit_request_changes_decision(
    glab: GlabClient,
    *,
    project_path: str,
    mr_iid: str,
    review_state: str | None,
    reviewer_added: bool,
) -> int:
    if review_state == "REQUESTED_CHANGES":
        return _emit_unchanged(mr_iid, reviewer_added, "REQUESTED_CHANGES")
    errors = _request_changes(glab, project_path, mr_iid)
    if errors:
        return _soft_reject(
            "; ".join(errors),
            mr_iid=mr_iid,
            reviewer_added=reviewer_added,
        )
    return _emit_decision(
        "requested_changes",
        mr_iid=mr_iid,
        reviewer_added=reviewer_added,
        message="requested-changes",
    )


def _submit_approve_decision(
    glab: GlabClient,
    *,
    mr_iid: str,
    review_state: str | None,
    reviewer_added: bool,
) -> int:
    if review_state == "APPROVED":
        return _emit_unchanged(mr_iid, reviewer_added, "APPROVED")
    reject_reason = _approve(glab, mr_iid)
    if reject_reason:
        return _soft_reject(
            reject_reason,
            mr_iid=mr_iid,
            reviewer_added=reviewer_added,
        )
    return _emit_decision(
        "approved",
        mr_iid=mr_iid,
        reviewer_added=reviewer_added,
        message="approved",
    )


def _submit_decision(
    glab: GlabClient,
    *,
    project_path: str,
    mr_iid: str,
    decision: Decision,
    review_state: str | None,
    reviewer_added: bool,
) -> int:
    if decision == "request-changes":
        return _submit_request_changes_decision(
            glab,
            project_path=project_path,
            mr_iid=mr_iid,
            review_state=review_state,
            reviewer_added=reviewer_added,
        )
    if decision == "approve":
        return _submit_approve_decision(
            glab,
            mr_iid=mr_iid,
            review_state=review_state,
            reviewer_added=reviewer_added,
        )
    return _emit_decision(
        "reviewer_only",
        mr_iid=mr_iid,
        reviewer_added=reviewer_added,
        message="reviewer-only",
    )
