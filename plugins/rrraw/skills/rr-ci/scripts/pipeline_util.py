from __future__ import annotations

from typing import Any

from errors import GlabError
from glab import GLAB_SINGLE_PAGE, GlabClient, api_list_pages

TERMINAL_PIPELINE_STATUSES = frozenset({"success", "failed", "manual", "canceled"})


def bridge_status_csv(bridges: list[dict[str, Any]] | Any) -> tuple[str, bool]:
    if not isinstance(bridges, list):
        return "", False
    bridge_csv = ",".join(f"{bridge.get('name')}:{bridge.get('status')}" for bridge in bridges)
    has_failed_bridge = any(bridge.get("status") == "failed" for bridge in bridges)
    return bridge_csv, has_failed_bridge


def failed_job_csv(jobs: list[dict[str, Any]] | Any) -> tuple[str, bool]:
    if not isinstance(jobs, list):
        return "", False
    names = [job.get("name", "") for job in jobs if job.get("status") == "failed"]
    return ",".join(names), bool(names)


def mr_latest_pipeline_status(
    glab: GlabClient, project_id: str, mr_iid: str
) -> tuple[str, str, str, str]:
    pipelines = glab.api(
        f"projects/{project_id}/merge_requests/{mr_iid}/pipelines?per_page={GLAB_SINGLE_PAGE}"
    )
    if not isinstance(pipelines, list) or not pipelines:
        return "none", "none", "", ""
    pid = str(pipelines[0]["id"])
    pstatus = glab.api(f"projects/{project_id}/pipelines/{pid}").get(
        "status", "unknown"
    )
    try:
        bridges = glab.api(f"projects/{project_id}/pipelines/{pid}/bridges")
    except GlabError:
        bridges = []
    bridge_csv, bridge_failed = bridge_status_csv(bridges)
    if bridge_failed:
        pstatus = "failed"
    jobs = api_list_pages(glab, f"projects/{project_id}/pipelines/{pid}/jobs")
    failed_jobs, jobs_failed = failed_job_csv(jobs)
    if jobs_failed:
        pstatus = "failed"
    return pid, pstatus, bridge_csv, failed_jobs
