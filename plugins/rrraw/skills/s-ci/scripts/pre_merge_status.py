"""Single pre-merge verdict envelope (checks/pipeline, security, threads, reviews)."""

from __future__ import annotations

import argparse
from typing import Any

import emit
from glab import GlabClient, api_list_pages, default_glab
from mr_common import auth_check as _auth_check
from mr_common import resolve_open_mr as _resolve_open_mr
from pipeline_security_reports import _fetch_pipeline_security_reports

COMMAND = "pre-merge-status"

_PIPELINE_OK = frozenset({"success", "manual", "skipped"})
_PIPELINE_PENDING = frozenset(
    {"created", "waiting_for_resource", "preparing", "pending", "running"}
)
_MERGEABLE_OK = frozenset({"mergeable", "can_be_merged", "unchecked", ""})
_HARD_MERGE = frozenset(
    {
        "conflict",
        "conflicting",
        "discussions_not_resolved",
        "not_approved",
        "ci_must_pass",
        "ci_still_running",
        "blocked_status",
        "draft_status",
        "requested_changes",
    }
)


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        COMMAND,
        help="One-shot pre-merge verdict (ready|blocked + blockers)",
        description=(
            "Compose pipeline/checks, security, unresolved threads, and "
            "reviews/approvals into one envelope. Result keys: verdict "
            "(ready|blocked), blockers[], plus compact pipeline/checks, "
            "security, unresolved_threads, reviews."
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


def _pipeline_blockers(pipe_status: str) -> list[str]:
    if pipe_status in _PIPELINE_PENDING:
        return [f"pipeline_pending:{pipe_status}"]
    if pipe_status in {"", "no_pipeline"}:
        return ["pipeline_missing"]
    if pipe_status == "unknown":
        return ["pipeline:unknown"]
    if pipe_status not in _PIPELINE_OK:
        return [f"pipeline:{pipe_status}"]
    return []


def _merge_status_blocker(detailed: str, blockers: list[str]) -> str | None:
    if not detailed or detailed in _MERGEABLE_OK or detailed not in _HARD_MERGE:
        return None
    if detailed in {"conflict", "conflicting"} and "has_conflicts" in blockers:
        return None
    if detailed == "discussions_not_resolved" and any(
        b.startswith("unresolved_threads:") for b in blockers
    ):
        return None
    if detailed == "not_approved" and any(b.startswith("approvals_") for b in blockers):
        return None
    if detailed in {"ci_must_pass", "ci_still_running"} and any(
        b.startswith("pipeline") for b in blockers
    ):
        return None
    return f"merge_status:{detailed}"


def assemble_verdict(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Build verdict envelope from a collected snapshot (pure; unit-testable)."""
    pipeline = dict(snapshot.get("pipeline") or {})
    if not pipeline and snapshot.get("checks"):
        pipeline = dict(snapshot["checks"])
    pipe_status = str(pipeline.get("status") or "").lower()

    blockers = _pipeline_blockers(pipe_status)

    if snapshot.get("has_conflicts"):
        blockers.append("has_conflicts")

    security = snapshot.get("security") or {}
    if security.get("merge_blocked"):
        blockers.append("security_merge_blocked")

    unresolved = int(snapshot.get("unresolved_threads") or 0)
    if unresolved > 0:
        blockers.append(f"unresolved_threads:{unresolved}")

    reviews = snapshot.get("reviews") or {}
    approvals_left = reviews.get("approvals_left")
    if isinstance(approvals_left, int) and approvals_left > 0:
        blockers.append(f"approvals_left:{approvals_left}")
    elif reviews.get("approved") is False and reviews.get("approvals_required"):
        blockers.append("approvals_missing")

    detailed = str(
        snapshot.get("detailed_merge_status") or snapshot.get("merge_status") or ""
    ).lower()
    merge_blocker = _merge_status_blocker(detailed, blockers)
    if merge_blocker:
        blockers.append(merge_blocker)

    result: dict[str, Any] = {
        "verdict": "ready" if not blockers else "blocked",
        "blockers": blockers,
        "pipeline": pipeline if pipeline else {"status": "unknown"},
        "security": {
            "merge_blocked": bool(security.get("merge_blocked")),
            "status": security.get("status") or "",
        },
        "unresolved_threads": unresolved,
        "reviews": {
            "summary": reviews.get("summary") or "",
            "approvals_left": reviews.get("approvals_left"),
            "approvals_required": reviews.get("approvals_required"),
            "approved": reviews.get("approved"),
        },
    }
    if "checks" in snapshot:
        result["checks"] = snapshot["checks"]
    return result


def _count_unresolved_threads(glab: GlabClient, mr_iid: str) -> int:
    discussions = api_list_pages(
        glab,
        f"projects/:fullpath/merge_requests/{mr_iid}/discussions",
    )
    return sum(1 for d in discussions if not d.get("resolved"))


def _pipeline_snapshot(mr: dict[str, Any]) -> dict[str, Any]:
    head = mr.get("head_pipeline") or mr.get("pipeline") or {}
    if not isinstance(head, dict) or not head:
        return {"status": "no_pipeline"}
    status = str(head.get("status") or "no_pipeline")
    out: dict[str, Any] = {"status": status}
    if head.get("id") is not None:
        out["id"] = str(head["id"])
    if head.get("iid") is not None:
        out["iid"] = str(head["iid"])
    return out


def _reviews_snapshot(
    glab: GlabClient, mr_iid: str, mr: dict[str, Any]
) -> dict[str, Any]:
    try:
        approvals = glab.api(f"projects/:fullpath/merge_requests/{mr_iid}/approvals")
    except Exception:
        approvals = {}
    if not isinstance(approvals, dict):
        approvals = {}
    required = approvals.get("approvals_required")
    left = approvals.get("approvals_left")
    approved_by = approvals.get("approved_by") or []
    approved = bool(approvals.get("approved")) if approvals else None
    if left is None and isinstance(required, int):
        got = len(approved_by) if isinstance(approved_by, list) else 0
        left = max(required - got, 0)
    summary_parts: list[str] = []
    if isinstance(required, int):
        summary_parts.append(f"required={required}")
    if isinstance(left, int):
        summary_parts.append(f"left={left}")
    if approved:
        summary_parts.append("approved")
    reviewers = mr.get("reviewers") or []
    if isinstance(reviewers, list) and reviewers:
        summary_parts.append(f"reviewers={len(reviewers)}")
    return {
        "approvals_required": required,
        "approvals_left": left,
        "approved": approved,
        "summary": ", ".join(summary_parts) if summary_parts else "unknown",
    }


def _security_snapshot(glab: GlabClient, mr_iid: str) -> dict[str, Any]:
    try:
        raw = _fetch_pipeline_security_reports(glab, mr_iid, None)
        return {
            "status": raw.get("status") or "",
            "merge_blocked": bool(raw.get("merge_blocked")),
        }
    except Exception as exc:
        return {"status": "unavailable", "merge_blocked": False, "note": str(exc)}


def _collect_gitlab(glab: GlabClient, mr_ref: str | None) -> dict[str, Any]:
    _auth_check(glab)
    mr = _resolve_open_mr(glab, mr_ref)
    iid = str(mr.get("iid", ""))

    pipeline = _pipeline_snapshot(mr)
    pipe_status = str(pipeline.get("status") or "").lower()
    # Prefer filling known fields; skip expensive security GraphQL on hard fail
    hard_fail = pipe_status not in _PIPELINE_OK and pipe_status not in _PIPELINE_PENDING

    snapshot: dict[str, Any] = {
        "mr_iid": iid,
        "pipeline": pipeline,
        "has_conflicts": bool(mr.get("has_conflicts")),
        "detailed_merge_status": str(mr.get("detailed_merge_status") or ""),
        "merge_status": str(mr.get("merge_status") or ""),
        "unresolved_threads": _count_unresolved_threads(glab, iid),
        "reviews": _reviews_snapshot(glab, iid, mr),
        "security": (
            {"status": "skipped", "merge_blocked": False}
            if hard_fail
            else _security_snapshot(glab, iid)
        ),
    }

    result = assemble_verdict(snapshot)
    result["mr_iid"] = iid
    return result


def main(*, mr_ref: str | None = None, glab: GlabClient | None = None) -> int:
    def _run() -> int:
        client = glab or default_glab()
        result = _collect_gitlab(client, mr_ref)
        return emit.succeed(COMMAND, result)

    return emit.run_guarded(COMMAND, _run)
