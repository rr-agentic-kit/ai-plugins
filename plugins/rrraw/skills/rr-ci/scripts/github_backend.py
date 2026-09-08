from __future__ import annotations

import json
from argparse import Namespace
from typing import Any

import emit
from errors import GitError
from forge import detect
from gh import GhClient, default_gh
from gitutil import current_branch, merge_base_refs, repo_root


def dispatch(args: Namespace) -> int:
    command = args.command
    try:
        client = default_gh()
        if command == "debug-pipeline":
            return _debug_pipeline(client, args)
        if command == "code-quality-reports":
            return _code_quality(client)
        if command == "pipeline-security-reports":
            return _security(client)
        if command == "mr-skip-threads":
            return _skip_threads(client, args)
        if command == "mr-add-preflight":
            return _add_preflight(client, args)
        if command == "mr-ensure-review-instructions":
            return _ensure_instructions(client, args)
        if command == "mr-ci-review-preflight":
            return _ci_preflight(client, args)
        if command == "mr-review-submit":
            return _review_submit(client, args)
        if command == "pending-reviews":
            return _pending(client)
        return emit.fail(command, "unknown_command", command)
    except FileNotFoundError as exc:
        return emit.fail_exception(command, exc)
    except Exception as exc:
        return emit.fail_exception(command, exc)


def _pr_number(client: GhClient, explicit: str | None) -> str:
    if explicit:
        return str(explicit)
    branch = current_branch()
    raw = client.cli(
        [
            "pr",
            "view",
            "--json",
            "number",
            "--jq",
            ".number",
            "--head",
            branch,
        ]
    )
    number = raw.strip()
    if not number:
        raise GitError(f"no open pull request for branch: {branch}")
    return number


def _debug_pipeline(client: GhClient, _args: Namespace) -> int:
    branch = current_branch()
    listing = client.cli(
        [
            "run",
            "list",
            "--branch",
            branch,
            "--limit",
            "1",
            "--json",
            "databaseId,status,conclusion,url,displayTitle,headSha",
        ]
    )
    runs = json.loads(listing) if listing.strip() else []
    if not runs:
        return emit.succeed(
            "debug-pipeline",
            {"status": "no_pipeline", "error_lines": [], "failed_job_id": ""},
        )
    run = runs[0]
    run_id = str(run.get("databaseId", ""))
    conclusion = str(run.get("conclusion") or run.get("status") or "")
    error_lines: list[str] = []
    failed_job_id = ""
    if conclusion in {"failure", "timed_out", "cancelled"}:
        try:
            log = client.cli(["run", "view", run_id, "--log-failed"])
            error_lines = [line for line in log.splitlines() if line.strip()][:40]
        except Exception:
            error_lines = []
        jobs_raw = client.cli(["run", "view", run_id, "--json", "jobs"])
        jobs = json.loads(jobs_raw).get("jobs") or []
        for job in jobs:
            if job.get("conclusion") == "failure":
                failed_job_id = str(job.get("databaseId") or job.get("name") or "")
                break
    status = "failed" if conclusion == "failure" else conclusion or "unknown"
    return emit.succeed(
        "debug-pipeline",
        {
            "status": status,
            "error_lines": error_lines,
            "failed_job_id": failed_job_id,
            "pipeline_id": run_id,
        },
    )


def _code_quality(client: GhClient) -> int:
    try:
        alerts = client.api("repos/{owner}/{repo}/code-scanning/alerts?state=open")
    except Exception:
        alerts = []
    nodes = alerts if isinstance(alerts, list) else []
    return emit.succeed(
        "code-quality-reports",
        {"reports": {"count": len(nodes), "nodes": nodes[:50]}},
    )


def _security(client: GhClient) -> int:
    scanning: list[Any] = []
    dependabot: list[Any] = []
    try:
        raw = client.api("repos/{owner}/{repo}/code-scanning/alerts?state=open")
        scanning = raw if isinstance(raw, list) else []
    except Exception:
        scanning = []
    try:
        raw = client.api("repos/{owner}/{repo}/dependabot/alerts?state=open")
        dependabot = raw if isinstance(raw, list) else []
    except Exception:
        dependabot = []
    nodes = list(scanning) + list(dependabot)
    blocking = [
        n
        for n in nodes
        if str(n.get("severity") or n.get("security_advisory", {}).get("severity", "")).lower()
        in {"critical", "high"}
    ]
    status = "clean" if not nodes else "blocking_findings" if blocking else "no_reports"
    if nodes and not blocking:
        status = "clean"
    return emit.succeed(
        "pipeline-security-reports",
        {
            "status": status if nodes or scanning or dependabot else "no_reports",
            "merge_blocked": bool(blocking),
            "findings": {
                "count": len(nodes),
                "nodes": nodes[:50],
                "blocking_count": len(blocking),
                "blocking_nodes": blocking[:20],
            },
        },
    )


_THREADS_QUERY = """
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100) {
        nodes { id isResolved }
      }
    }
  }
}
"""

_RESOLVE_MUTATION = """
mutation($id: ID!) {
  resolveReviewThread(input: {threadId: $id}) {
    thread { isResolved }
  }
}
"""


def _skip_threads(client: GhClient, args: Namespace) -> int:
    pr = _pr_number(client, getattr(args, "mr_iid", None))
    remote = detect()
    data = client.graphql(
        _THREADS_QUERY,
        {"owner": remote.owner, "name": remote.repo, "number": int(pr)},
    )
    nodes = (
        ((data or {}).get("repository") or {})
        .get("pullRequest", {})
        .get("reviewThreads", {})
        .get("nodes")
        or []
    )
    unresolved = [n for n in nodes if not n.get("isResolved")]
    if getattr(args, "dry_run", False):
        return emit.succeed(
            "mr-skip-threads",
            {
                "unresolved_count": len(unresolved),
                "ok_count": 0,
                "fail_count": 0,
            },
        )
    ok_count = 0
    fail_count = 0
    for node in unresolved:
        try:
            client.graphql(_RESOLVE_MUTATION, {"id": node["id"]})
            ok_count += 1
        except Exception:
            fail_count += 1
    remaining = fail_count
    return emit.succeed(
        "mr-skip-threads",
        {
            "unresolved_count": remaining,
            "ok_count": ok_count,
            "fail_count": fail_count,
        },
    )


def _add_preflight(client: GhClient, args: Namespace) -> int:
    repo_root()
    branch = getattr(args, "branch_name", None) or current_branch()
    try:
        url = client.cli(
            ["pr", "view", "--json", "url", "--jq", ".url", "--head", branch]
        ).strip()
        if url:
            return emit.succeed(
                "mr-add-preflight",
                {"status": "exists", "mr_url": url, "message": "PR already exists"},
            )
    except Exception:
        pass
    return emit.succeed(
        "mr-add-preflight",
        {
            "status": "ready_create",
            "message": "no open PR for branch",
            "upstream": branch,
        },
    )


def _ensure_instructions(_client: GhClient, args: Namespace) -> int:
    if getattr(args, "dry_run", False):
        return emit.succeed(
            "mr-ensure-review-instructions",
            {"action": "would-post"},
        )
    return emit.succeed(
        "mr-ensure-review-instructions",
        {"action": "skipped_github_no_marker"},
    )


def _ci_preflight(client: GhClient, args: Namespace) -> int:
    pr = getattr(args, "mr_ref", None) or getattr(args, "mr_iid", None)
    number = _pr_number(client, str(pr) if pr else None)
    payload = json.loads(
        client.cli(
            [
                "pr",
                "view",
                number,
                "--json",
                "number,baseRefName,headRefName,url",
            ]
        )
    )
    head = payload.get("headRefName") or current_branch()
    base = payload.get("baseRefName") or "main"
    merge_base = merge_base_refs(f"origin/{base}", "HEAD")
    return emit.succeed(
        "mr-ci-review-preflight",
        {
            "mr_iid": str(payload.get("number") or number),
            "source_branch": head,
            "target_branch": base,
            "merge_base": merge_base,
            "head_ref": "HEAD",
            "read_ref": "HEAD",
            "ref_range": f"{merge_base}..HEAD",
            "allowlist": [],
            "scope": "full",
            "diff_refs": {},
        },
    )


def _review_submit(client: GhClient, args: Namespace) -> int:
    pr = _pr_number(client, getattr(args, "mr_iid", None))
    decision = getattr(args, "decision", "none")
    dry = getattr(args, "dry_run", False)
    if dry:
        return emit.succeed(
            "mr-review-submit",
            {
                "status": "would-submit",
                "reviewer_added": False,
                "mr_iid": pr,
            },
        )
    if decision == "approve":
        client.cli(["pr", "review", pr, "--approve"])
        status = "approved"
    elif decision == "request-changes":
        client.cli(["pr", "review", pr, "--request-changes", "--body", "Requested changes"])
        status = "requested_changes"
    else:
        status = "reviewer_only"
    return emit.succeed(
        "mr-review-submit",
        {"status": status, "reviewer_added": False, "mr_iid": pr},
    )


def _pending(client: GhClient) -> int:
    raw = client.cli(
        [
            "search",
            "prs",
            "--review-requested=@me",
            "--state=open",
            "--json",
            "url",
            "--limit",
            "50",
        ]
    )
    items = json.loads(raw) if raw.strip() else []
    urls = [str(item.get("url")) for item in items if item.get("url")]
    return emit.succeed("pending-reviews", {"count": len(urls), "urls": urls})
