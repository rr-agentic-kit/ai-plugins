from __future__ import annotations

import argparse
import subprocess
import sys
from typing import Any

import emit
from ci_url import CiUrl, is_ci_url, parse_ci_url_or_raise
from errors import CiUrlError, GlabError
from gitutil import current_branch
from glab import GLAB_SINGLE_PAGE, GlabClient, api_list_pages, default_glab
from job_trace import filter_error_lines
from paths import ci_artifacts_dir, ci_file, ci_rel

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
                "failed_step": "",
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
            "failed_step": failed.get("failed_step", ""),
            "failed_source": f"bridge:{bridge_name}",
        }

    try:
        bridges = glab.api(f"projects/:fullpath/pipelines/{pipeline_id}/bridges")
    except GlabError:
        bridges = []

    return _scan_bridge_failures(glab, bridges)


def _pipeline_run_url(glab: GlabClient, pipeline_id: str) -> str:
    try:
        payload = glab.api(f"projects/:fullpath/pipelines/{pipeline_id}")
        return str(payload.get("web_url") or "")
    except GlabError:
        return ""


def _job_by_id(glab: GlabClient, job_id: str) -> dict[str, Any]:
    payload = glab.api(f"projects/:fullpath/jobs/{job_id}")
    if not isinstance(payload, dict):
        raise GlabError(f"unexpected job payload for {job_id}")
    return payload


def _download_gitlab_artifacts(glab: GlabClient, job_id: str, dest_dir: Any) -> None:
    zip_path = dest_dir / "artifacts.zip"
    result = subprocess.run(
        ["glab", "api", f"projects/:fullpath/jobs/{job_id}/artifacts"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise GlabError(
            f"glab artifact download failed for job {job_id}",
            stderr=result.stderr.decode("utf-8", errors="replace"),
        )
    zip_path.write_bytes(result.stdout)


def _report_failed_job(
    client: GlabClient,
    pipeline_id: str | None,
    failed: dict[str, str],
    *,
    save_log: bool,
    artifacts: bool,
    run_url: str = "",
) -> int:
    trace = client.cli(["ci", "trace", failed["failed_job_id"]])
    error_lines = filter_error_lines(trace)
    result = _failed_job_result(
        client,
        failed,
        error_lines,
        trace,
        save_log=save_log,
        artifacts=artifacts,
        run_url=run_url,
        pipeline_id=pipeline_id,
    )
    _print_error_lines(error_lines)
    return emit.succeed(COMMAND, result, exit_code=1)


def _failed_job_result(
    client: GlabClient,
    failed: dict[str, str],
    error_lines: list[str],
    trace: str,
    *,
    save_log: bool,
    artifacts: bool = False,
    run_url: str = "",
    pipeline_id: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "failed_job",
        "failed_job_id": failed["failed_job_id"],
        "failed_job_name": failed.get("failed_job_name", ""),
        "failed_step": failed.get("failed_step", ""),
        "error_lines": error_lines,
    }
    if run_url:
        result["run_url"] = run_url
    if pipeline_id:
        result["pipeline_id"] = pipeline_id
    if save_log:
        path = ci_file(f"job-{failed['failed_job_id']}.log")
        path.write_text(trace, encoding="utf-8")
        result["log_path"] = ci_rel(path)
    if artifacts:
        dest = ci_artifacts_dir(failed["failed_job_id"])
        _download_gitlab_artifacts(client, failed["failed_job_id"], dest)
        result["artifacts_dir"] = ci_rel(dest)
    return result


def _print_error_lines(error_lines: list[str]) -> None:
    print("=== Error Messages (filtered) ===", file=sys.stderr)
    for line in error_lines:
        print(line, file=sys.stderr)


def _resolve_gitlab_target(
    ref: str | None,
    run_id: str | None,
    job_id: str | None,
) -> tuple[CiUrl | None, str | None, str | None, str | None]:
    if ref and is_ci_url(ref):
        parsed = parse_ci_url_or_raise(ref)
        if parsed.forge != "gitlab":
            raise CiUrlError(
                "forge_mismatch", f"URL forge is {parsed.forge}, expected gitlab"
            )
        return (
            parsed,
            run_id or parsed.run_id,
            job_id or parsed.job_id,
            None,
        )
    return None, run_id, job_id, ref


def _debug_job_direct(
    client: GlabClient,
    job_id: str,
    *,
    save_log: bool,
    artifacts: bool,
) -> int:
    job = _job_by_id(client, job_id)
    pipeline = job.get("pipeline") or {}
    pipeline_id = str(pipeline.get("id") or "") or None
    run_url = str(
        pipeline.get("web_url") or _pipeline_run_url(client, pipeline_id or "")
    )
    failed = {
        "failed_job_id": job_id,
        "failed_job_name": str(job.get("name") or ""),
        "failed_step": "",
        "failed_source": "job_url",
    }
    if job.get("status") != "failed":
        return emit.succeed(
            COMMAND,
            {
                "status": "no_failed_job",
                "failed_job_id": job_id,
                "failed_job_name": failed["failed_job_name"],
                "error_lines": [],
                "run_url": run_url,
            },
        )
    return _report_failed_job(
        client,
        pipeline_id,
        failed,
        save_log=save_log,
        artifacts=artifacts,
        run_url=run_url,
    )


def _debug_pipeline_or_fail(
    client: GlabClient,
    mr_iid: str | None,
    *,
    pipeline_id: str | None,
    save_log: bool,
    artifacts: bool,
) -> int:
    resolved_pipeline_id = pipeline_id or _find_pipeline_id(client, mr_iid)
    if not resolved_pipeline_id:
        return emit.fail(COMMAND, "no_pipeline", "no pipeline found")

    run_url = _pipeline_run_url(client, resolved_pipeline_id)
    try:
        pipeline = client.api(f"projects/:fullpath/pipelines/{resolved_pipeline_id}")
    except GlabError:
        pipeline = {}
    pipe_status = str(pipeline.get("status") or "")
    if pipe_status == "success":
        return emit.succeed(
            COMMAND,
            {
                "status": "success",
                "error_lines": [],
                "failed_job_id": "",
                "run_url": run_url,
                "pipeline_id": resolved_pipeline_id,
            },
        )
    if pipe_status in {
        "running",
        "pending",
        "created",
        "waiting_for_resource",
        "preparing",
    }:
        return emit.succeed(
            COMMAND,
            {
                "status": "running",
                "error_lines": [],
                "failed_job_id": "",
                "run_url": run_url,
                "pipeline_id": resolved_pipeline_id,
            },
        )

    failed = _find_failed_job(client, resolved_pipeline_id)
    if not failed:
        return emit.fail(
            COMMAND,
            "no_failed_job",
            "no failed jobs found",
            result={
                "status": "no_failed_job",
                "run_url": run_url,
                "pipeline_id": resolved_pipeline_id,
            },
        )

    return _report_failed_job(
        client,
        resolved_pipeline_id,
        failed,
        save_log=save_log,
        artifacts=artifacts,
        run_url=run_url,
    )


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        COMMAND,
        help="Debug first failed job on current branch, MR, or explicit run/job URL",
        description=(
            "Result keys: status, failed_job_id, failed_job_name, failed_step, "
            "error_lines, run_url, log_path, artifacts_dir"
        ),
    )
    parser.add_argument(
        "ref",
        nargs="?",
        help="Optional MR IID, PR number, or run/job URL",
    )
    parser.add_argument("--run-id", help="Explicit pipeline/run id")
    parser.add_argument("--job-id", help="Explicit job id")
    parser.add_argument(
        "--save-log",
        action="store_true",
        help="Write full job trace to .ai/ci/job-<id>.log",
    )
    parser.add_argument(
        "--artifacts",
        action="store_true",
        help="Download job artifacts to .ai/ci/artifacts/<id>/",
    )
    parser.set_defaults(handler=_handler)


def _handler(args: argparse.Namespace) -> int:
    return main(
        ref=getattr(args, "ref", None),
        run_id=getattr(args, "run_id", None),
        job_id=getattr(args, "job_id", None),
        save_log=args.save_log,
        artifacts=getattr(args, "artifacts", False),
    )


def main(
    *,
    ref: str | None = None,
    run_id: str | None = None,
    job_id: str | None = None,
    save_log: bool = False,
    artifacts: bool = False,
    glab: GlabClient | None = None,
) -> int:
    def _run() -> int:
        client = glab or default_glab()
        try:
            _parsed, resolved_run_id, resolved_job_id, mr_iid = _resolve_gitlab_target(
                ref, run_id, job_id
            )
        except CiUrlError as exc:
            return emit.fail(COMMAND, exc.code, str(exc))

        if resolved_job_id and ((ref and is_ci_url(ref)) or job_id):
            return _debug_job_direct(
                client,
                resolved_job_id,
                save_log=save_log,
                artifacts=artifacts,
            )

        return _debug_pipeline_or_fail(
            client,
            mr_iid,
            pipeline_id=resolved_run_id,
            save_log=save_log,
            artifacts=artifacts,
        )

    return emit.run_guarded(COMMAND, _run)
