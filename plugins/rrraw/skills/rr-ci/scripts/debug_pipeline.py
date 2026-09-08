from __future__ import annotations

import argparse
import sys
from typing import Any

import emit
from errors import GlabError
from gitutil import current_branch
from glab import GLAB_SINGLE_PAGE, GlabClient, api_list_pages, default_glab
from job_trace import filter_error_lines

COMMAND = "debug-pipeline"


def _find_pipeline_id(glab: GlabClient, mr_iid: str | None) -> str | None:
    if mr_iid:
        pipelines = glab.api(
            f"projects/:fullpath/merge_requests/{mr_iid}/pipelines?per_page={GLAB_SINGLE_PAGE}"
        )
    else:
        ref = current_branch()
        pipelines = glab.api(
            f"projects/:fullpath/pipelines?ref={ref}&per_page={GLAB_SINGLE_PAGE}"
        )
    if isinstance(pipelines, list) and pipelines:
        pid = pipelines[0].get("id")
        return str(pid) if pid is not None else None
    return None


def _failed_job_from_jobs(jobs: list[dict[str, Any]] | Any) -> dict[str, str] | None:
    if not isinstance(jobs, list):
        return None
    for job in jobs:
        if job.get("status") == "failed":
            return {
                "failed_job_id": str(job["id"]),
                "failed_job_name": str(job.get("name", "")),
                "failed_source": "job",
            }
    return None


def _failed_child_from_bridge(
    glab: GlabClient,
    bridge: dict[str, Any],
) -> dict[str, str] | None:
    bstatus = bridge.get("status")
    bname = bridge.get("name", "")
    downstream = bridge.get("downstream_pipeline") or {}
    downstream_id = downstream.get("id")
    if not downstream_id:
        return None
    downstream_id_str = str(downstream_id)
    if bstatus == "failed":
        return _first_failed_child(glab, downstream_id_str, bname)
    try:
        ds = glab.api(f"projects/:fullpath/pipelines/{downstream_id_str}")
        if ds.get("status") == "failed":
            return _first_failed_child(glab, downstream_id_str, bname)
    except GlabError:
        return None
    return None


def _scan_bridge_failures(
    glab: GlabClient,
    bridges: list[dict[str, Any]] | Any,
) -> dict[str, str] | None:
    if not isinstance(bridges, list):
        return None

    for bridge in bridges:
        child = _failed_child_from_bridge(glab, bridge)
        if child:
            return child
    return None


def _find_failed_job(glab: GlabClient, pipeline_id: str) -> dict[str, str] | None:
    jobs = api_list_pages(glab, f"projects/:fullpath/pipelines/{pipeline_id}/jobs")
    failed = _failed_job_from_jobs(jobs)
    if failed:
        return failed

    try:
        bridges = glab.api(f"projects/:fullpath/pipelines/{pipeline_id}/bridges")
    except GlabError:
        bridges = []

    return _scan_bridge_failures(glab, bridges)


def _first_failed_child(
    glab: GlabClient, pipeline_id: str, bridge_name: str
) -> dict[str, str] | None:
    try:
        jobs = api_list_pages(glab, f"projects/:fullpath/pipelines/{pipeline_id}/jobs")
    except GlabError:
        return None

    failed = _failed_job_from_jobs(jobs)
    if failed:
        return {
            "failed_job_id": failed["failed_job_id"],
            "failed_job_name": failed["failed_job_name"],
            "failed_source": f"bridge:{bridge_name}",
        }

    try:
        bridges = glab.api(f"projects/:fullpath/pipelines/{pipeline_id}/bridges")
    except GlabError:
        bridges = []

    return _scan_bridge_failures(glab, bridges)


def _report_failed_job(
    client: GlabClient,
    _pipeline_id: str,
    failed: dict[str, str],
    *,
    save_log: bool,
) -> int:
    trace = client.cli(["ci", "trace", failed["failed_job_id"]])
    error_lines = filter_error_lines(trace)
    result = _failed_job_result(failed, error_lines, trace, save_log=save_log)
    _print_error_lines(error_lines)
    return emit.succeed(COMMAND, result, exit_code=1)


def _failed_job_result(
    failed: dict[str, str],
    error_lines: list[str],
    trace: str,
    *,
    save_log: bool,
) -> dict[str, Any]:
    if save_log:
        log_file = f"job-{failed['failed_job_id']}.log"
        with open(log_file, "w", encoding="utf-8") as handle:
            handle.write(trace)
    return {
        "status": "failed_job",
        "failed_job_id": failed["failed_job_id"],
        "error_lines": error_lines,
    }


def _print_error_lines(error_lines: list[str]) -> None:
    print("=== Error Messages (filtered) ===", file=sys.stderr)
    for line in error_lines:
        print(line, file=sys.stderr)


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        COMMAND,
        help="Debug first failed job on current branch or MR pipeline",
        description="Result keys: status, failed_job_id, error_lines",
    )
    parser.add_argument("mr_iid", nargs="?", help="Optional merge request IID")
    parser.add_argument(
        "--save-log",
        action="store_true",
        help="Write full job trace to job-<id>.log",
    )
    parser.set_defaults(handler=_handler)


def _handler(args: argparse.Namespace) -> int:
    return main(mr_iid=args.mr_iid, save_log=args.save_log)


def _debug_pipeline_or_fail(
    client: GlabClient,
    mr_iid: str | None,
    *,
    save_log: bool,
) -> int:
    pipeline_id = _find_pipeline_id(client, mr_iid)
    if not pipeline_id:
        return emit.fail(COMMAND, "no_pipeline", "no pipeline found")

    failed = _find_failed_job(client, pipeline_id)
    if not failed:
        return emit.fail(
            COMMAND,
            "no_failed_job",
            "no failed jobs found",
            result={"status": "no_failed_job"},
        )

    return _report_failed_job(client, pipeline_id, failed, save_log=save_log)


def main(
    *,
    mr_iid: str | None = None,
    save_log: bool = False,
    glab: GlabClient | None = None,
) -> int:
    def _run() -> int:
        client = glab or default_glab()
        return _debug_pipeline_or_fail(client, mr_iid, save_log=save_log)

    return emit.run_guarded(COMMAND, _run)
