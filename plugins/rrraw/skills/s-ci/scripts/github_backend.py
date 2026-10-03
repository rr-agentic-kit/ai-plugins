from __future__ import annotations

import json
from argparse import Namespace
from typing import Any

import emit
from ci_url import CiUrl, is_ci_url, parse_ci_url_or_raise
from errors import CiUrlError, GhError, GitError
from forge import detect
from gh import GhClient, default_gh
from gitutil import current_branch, merge_base_refs, repo_root, resolve_pr_base
from job_trace import filter_error_lines
from mr_inline_anchors import parse_unified_diff_plus_lines
from paths import ci_artifacts_dir, ci_file, ci_rel
from pre_merge_status import assemble_verdict


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
        if command == "mr-inline-anchors":
            return _inline_anchors(client, args)
        if command == "mr-review-submit":
            return _review_submit(client, args)
        if command == "pending-reviews":
            return _pending(client)
        if command == "pre-merge-status":
            return _pre_merge(client, args)
        return emit.fail(command, "unknown_command", command)
    except FileNotFoundError as exc:
        return emit.fail_exception(command, exc)
    except Exception as exc:
        return emit.fail_exception(command, exc)


def _gh_no_open_pr(exc: GhError) -> bool:
    """True when gh pr view failed because the branch has no open PR."""
    text = f"{exc} {exc.stderr}".lower()
    return "no pull requests found" in text


def _pr_number(client: GhClient, explicit: str | None) -> str:
    if explicit:
        return str(explicit)
    branch = current_branch()
    # `gh pr view` takes branch as positional; `--head` is not a valid flag.
    raw = client.cli(
        [
            "pr",
            "view",
            branch,
            "--json",
            "number",
            "--jq",
            ".number",
        ]
    )
    number = raw.strip()
    if not number:
        raise GitError(f"no open pull request for branch: {branch}")
    return number


def _github_repo_flags(owner: str | None, repo: str | None) -> list[str]:
    if owner and repo:
        return ["--repo", f"{owner}/{repo}"]
    return []


def _normalize_github_status(conclusion: str | None, status: str | None) -> str:
    normalized = (conclusion or "").lower()
    run_status = (status or "").lower()
    if normalized in {"failure", "timed_out", "cancelled"}:
        return "failed_job"
    if normalized == "success":
        return "success"
    if not conclusion and run_status in {
        "in_progress",
        "queued",
        "pending",
        "waiting",
        "requested",
    }:
        return "running"
    if not conclusion:
        return "running"
    return "success"


def _failed_step_from_job(job: dict[str, Any]) -> str:
    for step in job.get("steps") or []:
        if step.get("conclusion") == "failure":
            return str(step.get("name") or "")
    return ""


def _find_failed_github_job(
    jobs: list[dict[str, Any]], *, job_id: str | None = None
) -> dict[str, str] | None:
    for job in jobs:
        database_id = str(job.get("databaseId") or job.get("id") or "")
        if job_id and database_id != str(job_id):
            continue
        if job.get("conclusion") == "failure":
            return {
                "failed_job_id": database_id,
                "failed_job_name": str(job.get("name") or ""),
                "failed_step": _failed_step_from_job(job),
            }
    return None


def _resolve_github_target(
    ref: str | None,
    run_id: str | None,
    job_id: str | None,
) -> tuple[CiUrl | None, str | None, str | None, str | None, list[str]]:
    repo_flags: list[str] = []
    if ref and is_ci_url(ref):
        parsed = parse_ci_url_or_raise(ref)
        if parsed.forge != "github":
            raise CiUrlError(
                "forge_mismatch", f"URL forge is {parsed.forge}, expected github"
            )
        repo_flags = _github_repo_flags(parsed.owner, parsed.repo)
        return (
            parsed,
            run_id or parsed.run_id,
            job_id or parsed.job_id,
            None,
            repo_flags,
        )
    return None, run_id, job_id, ref, repo_flags


def _github_run_view(
    client: GhClient,
    run_id: str,
    *,
    repo_flags: list[str],
    fields: str,
) -> dict[str, Any]:
    raw = client.cli(
        ["run", "view", run_id, *repo_flags, "--json", fields],
    )
    payload = json.loads(raw) if raw.strip() else {}
    return payload if isinstance(payload, dict) else {}


def _github_jobs(
    client: GhClient,
    run_id: str,
    *,
    repo_flags: list[str],
) -> list[dict[str, Any]]:
    payload = _github_run_view(
        client,
        run_id,
        repo_flags=repo_flags,
        fields="jobs",
    )
    jobs = payload.get("jobs") or []
    return jobs if isinstance(jobs, list) else []


def _download_github_artifacts(
    client: GhClient,
    run_id: str,
    dest_dir: Any,
    *,
    repo_flags: list[str],
) -> None:
    client.cli(["run", "download", run_id, "-D", str(dest_dir), *repo_flags])


def _debug_pipeline(client: GhClient, args: Namespace) -> int:
    command = "debug-pipeline"
    ref = getattr(args, "ref", None)
    explicit_run_id = getattr(args, "run_id", None)
    explicit_job_id = getattr(args, "job_id", None)
    save_log = getattr(args, "save_log", False)
    artifacts = getattr(args, "artifacts", False)

    try:
        _parsed, run_id, job_id, _pr_ref, repo_flags = _resolve_github_target(
            ref, explicit_run_id, explicit_job_id
        )
    except CiUrlError as exc:
        return emit.fail(command, exc.code, str(exc))

    if not run_id:
        branch = current_branch()
        listing = client.cli(
            [
                "run",
                "list",
                "--branch",
                branch,
                *repo_flags,
                "--limit",
                "1",
                "--json",
                "databaseId,status,conclusion,url,displayTitle,headSha",
            ]
        )
        runs = json.loads(listing) if listing.strip() else []
        if not runs:
            return emit.succeed(
                command,
                {"status": "no_pipeline", "error_lines": [], "failed_job_id": ""},
            )
        run = runs[0]
        run_id = str(run.get("databaseId", ""))
    else:
        run = _github_run_view(
            client,
            run_id,
            repo_flags=repo_flags,
            fields="databaseId,status,conclusion,url,displayTitle,headSha",
        )

    run_url = str(run.get("url") or "")
    conclusion = str(run.get("conclusion") or "")
    run_status = str(run.get("status") or "")
    status = _normalize_github_status(conclusion or None, run_status or None)

    if status in {"success", "running"}:
        return emit.succeed(
            command,
            {
                "status": status,
                "error_lines": [],
                "failed_job_id": "",
                "run_url": run_url,
                "pipeline_id": run_id,
            },
        )

    jobs = _github_jobs(client, run_id, repo_flags=repo_flags)
    failed = _find_failed_github_job(jobs, job_id=job_id)
    if not failed:
        return emit.fail(
            command,
            "no_failed_job",
            "no failed jobs found",
            result={
                "status": "no_failed_job",
                "error_lines": [],
                "failed_job_id": "",
                "run_url": run_url,
                "pipeline_id": run_id,
            },
        )

    full_log = ""
    error_lines: list[str] = []
    log_args = ["run", "view", run_id, *repo_flags]
    if job_id:
        log_args.extend(["--job", str(job_id), "--log"])
    else:
        log_args.append("--log-failed")
    try:
        full_log = client.cli(log_args)
        error_lines = filter_error_lines(full_log)
    except Exception:
        error_lines = []

    result: dict[str, Any] = {
        "status": "failed_job",
        "error_lines": error_lines,
        "failed_job_id": failed["failed_job_id"],
        "failed_job_name": failed["failed_job_name"],
        "failed_step": failed["failed_step"],
        "run_url": run_url,
        "pipeline_id": run_id,
    }
    if save_log and full_log:
        stem = failed["failed_job_id"] or run_id or "unknown"
        path = ci_file(f"job-{stem}.log")
        path.write_text(full_log, encoding="utf-8")
        result["log_path"] = ci_rel(path)
    if artifacts:
        dest = ci_artifacts_dir(failed["failed_job_id"] or run_id)
        _download_github_artifacts(client, run_id, dest, repo_flags=repo_flags)
        result["artifacts_dir"] = ci_rel(dest)
    return emit.succeed(command, result, exit_code=1)


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
        if str(
            n.get("severity") or n.get("security_advisory", {}).get("severity", "")
        ).lower()
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
    nodes = ((data or {}).get("repository") or {}).get("pullRequest", {}).get(
        "reviewThreads", {}
    ).get("nodes") or []
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
    base_branch = resolve_pr_base(getattr(args, "base", None))
    try:
        # `gh pr view` takes branch as positional; `--head` is not a valid flag.
        url = client.cli(
            ["pr", "view", branch, "--json", "url", "--jq", ".url"]
        ).strip()
        if url:
            return emit.succeed(
                "mr-add-preflight",
                {
                    "status": "exists",
                    "mr_url": url,
                    "base_branch": base_branch,
                    "message": "PR already exists",
                },
            )
    except GhError as exc:
        if not _gh_no_open_pr(exc):
            raise
        # No open PR for branch → create path.
    return emit.succeed(
        "mr-add-preflight",
        {
            "status": "ready_create",
            "message": "no open PR for branch",
            "upstream": branch,
            "base_branch": base_branch,
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


def _inline_anchors(client: GhClient, args: Namespace) -> int:
    """Parse PR file patches for + lines when available; else parity-gap note."""
    pr = getattr(args, "mr_ref", None) or getattr(args, "mr_iid", None)
    number = _pr_number(client, str(pr) if pr else None)
    path_filter = frozenset(getattr(args, "paths", None) or [])
    try:
        meta = json.loads(
            client.cli(
                [
                    "pr",
                    "view",
                    number,
                    "--json",
                    "number,baseRefOid,headRefOid",
                ]
            )
        )
        files_raw = client.api(
            f"repos/{{owner}}/{{repo}}/pulls/{number}/files?per_page=100"
        )
    except Exception:
        return emit.succeed(
            "mr-inline-anchors",
            {
                "mr_iid": number,
                "diff_refs": {},
                "files": {},
                "note": (
                    "GitHub parity gap: could not load PR patches for + line anchors; "
                    "use gh pr diff / review comment line from the UI, or GitLab backend"
                ),
            },
        )

    files_list = files_raw if isinstance(files_raw, list) else []
    files: dict[str, list[int]] = {}
    for item in files_list:
        if not isinstance(item, dict):
            continue
        path = str(item.get("filename") or "")
        if not path:
            continue
        if path_filter and path not in path_filter:
            continue
        patch = str(item.get("patch") or "")
        if not patch:
            files.setdefault(path, [])
            continue
        files[path] = parse_unified_diff_plus_lines(patch)

    base_sha = str(meta.get("baseRefOid") or "")
    head_sha = str(meta.get("headRefOid") or "")
    diff_refs: dict[str, str] = {}
    if base_sha:
        diff_refs["base_sha"] = base_sha
        diff_refs["start_sha"] = base_sha  # GitHub has no GitLab start_sha; mirror base
    if head_sha:
        diff_refs["head_sha"] = head_sha

    result: dict[str, Any] = {
        "mr_iid": str(meta.get("number") or number),
        "diff_refs": diff_refs,
        "files": files,
    }
    if not files and not diff_refs:
        result["note"] = (
            "GitHub parity gap: empty PR files/patches; "
            "diff_refs may be incomplete vs GitLab"
        )
    return emit.succeed("mr-inline-anchors", result)


def _unresolved_thread_count(client: GhClient, pr: str) -> int:
    remote = detect()
    data = client.graphql(
        _THREADS_QUERY,
        {"owner": remote.owner, "name": remote.repo, "number": int(pr)},
    )
    nodes = ((data or {}).get("repository") or {}).get("pullRequest", {}).get(
        "reviewThreads", {}
    ).get("nodes") or []
    return sum(1 for n in nodes if not n.get("isResolved"))


def _pre_merge(client: GhClient, args: Namespace) -> int:
    pr_ref = getattr(args, "mr_ref", None) or getattr(args, "mr_iid", None)
    number = _pr_number(client, str(pr_ref) if pr_ref else None)
    payload = json.loads(
        client.cli(
            [
                "pr",
                "view",
                number,
                "--json",
                "number,mergeable,reviewDecision,statusCheckRollup,reviews",
            ]
        )
    )

    rollup = payload.get("statusCheckRollup") or []
    check_status = "success"
    failing: list[str] = []
    if isinstance(rollup, list) and rollup:
        for item in rollup:
            state = str(
                item.get("conclusion") or item.get("state") or item.get("status") or ""
            ).upper()
            if state in {"FAILURE", "FAILED", "ERROR", "CANCELLED", "TIMED_OUT"}:
                check_status = "failure"
                name = str(item.get("name") or item.get("context") or "check")
                failing.append(name)
            elif (
                state in {"PENDING", "QUEUED", "IN_PROGRESS", "EXPECTED"}
                and check_status != "failure"
            ):
                check_status = "pending"
    else:
        check_status = "no_pipeline"

    mergeable = str(payload.get("mergeable") or "").upper()
    has_conflicts = mergeable == "CONFLICTING"

    # Security via same logic as _security, compact
    security_status = "clean"
    merge_blocked = False
    try:
        scanning = client.api("repos/{owner}/{repo}/code-scanning/alerts?state=open")
        nodes = scanning if isinstance(scanning, list) else []
        blocking = [
            n
            for n in nodes
            if str(n.get("severity") or "").lower() in {"critical", "high"}
        ]
        merge_blocked = bool(blocking)
        if merge_blocked:
            security_status = "blocking_findings"
        elif not nodes:
            security_status = "no_reports"
    except Exception:
        security_status = "unavailable"

    unresolved = _unresolved_thread_count(client, number)
    decision = str(payload.get("reviewDecision") or "")
    reviews_raw = payload.get("reviews") or []
    approved = decision.upper() == "APPROVED"
    changes_requested = decision.upper() == "CHANGES_REQUESTED"
    reviews = {
        "summary": decision
        or f"reviews={len(reviews_raw) if isinstance(reviews_raw, list) else 0}",
        "approved": approved if decision else None,
        "approvals_required": None,
        "approvals_left": (
            1 if changes_requested or (decision.upper() == "REVIEW_REQUIRED") else 0
        ),
    }

    snapshot: dict[str, Any] = {
        "checks": {"status": check_status, "failing": failing},
        "pipeline": {"status": check_status},
        "has_conflicts": has_conflicts,
        "security": {"status": security_status, "merge_blocked": merge_blocked},
        "unresolved_threads": unresolved,
        "reviews": reviews,
        "merge_status": mergeable.lower() if mergeable else "",
    }
    result = assemble_verdict(snapshot)
    result["mr_iid"] = str(payload.get("number") or number)
    return emit.succeed("pre-merge-status", result)


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
        client.cli(
            ["pr", "review", pr, "--request-changes", "--body", "Requested changes"]
        )
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
