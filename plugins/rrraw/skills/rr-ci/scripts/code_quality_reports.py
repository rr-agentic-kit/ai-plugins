from __future__ import annotations

import argparse
import sys
from typing import Any
from urllib.parse import quote

import emit
from errors import GlabError
from gitutil import current_branch, require_worktree
from glab import GLAB_LIST_PAGE_SIZE, GLAB_SINGLE_PAGE, GlabClient, default_glab
from mr_common import project_path as _project_path

COMMAND = "code-quality-reports"
_CODE_QUALITY_QUERY = f"""
query($fullPath: ID!, $iid: ID!, $after: String) {{
  project(fullPath: $fullPath) {{
    pipeline(iid: $iid) {{
      codeQualityReports(first: {GLAB_LIST_PAGE_SIZE}, after: $after) {{
        count
        nodes {{ description severity path line fingerprint webUrl }}
        pageInfo {{ endCursor hasNextPage }}
      }}
    }}
  }}
}}"""


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        COMMAND,
        help="Fetch CI-published code quality reports for a pipeline",
        description="Result keys: reports (count, nodes)",
    )
    parser.add_argument("ref", nargs="?", help="Git ref (default: current branch)")
    parser.add_argument(
        "pipeline_iid", nargs="?", help="Pipeline IID (default: latest for ref)"
    )
    parser.set_defaults(handler=_handler)


def _handler(args: argparse.Namespace) -> int:
    return main(ref=args.ref, pipeline_iid=args.pipeline_iid)


def _resolve_ref(ref: str | None) -> str:
    if ref:
        return ref
    require_worktree()
    return current_branch()


def _resolve_pipeline_iid(glab: GlabClient, ref: str, pipeline_iid: str | None) -> str:
    if pipeline_iid:
        return pipeline_iid
    encoded_ref = quote(ref, safe="")
    pipelines = glab.api(
        f"projects/:fullpath/pipelines?ref={encoded_ref}&per_page={GLAB_SINGLE_PAGE}"
    )
    if isinstance(pipelines, list) and pipelines:
        iid = pipelines[0].get("iid")
        if iid is not None:
            return str(iid)
    raise GlabError(f"no pipeline found for ref: {ref}")


def _fetch_reports(
    glab: GlabClient, project_path: str, pipeline_iid: str
) -> dict[str, Any]:
    all_nodes: list[dict[str, Any]] = []
    after: str | None = None
    count = 0
    while True:
        data = glab.graphql(
            _CODE_QUALITY_QUERY,
            variables={"fullPath": project_path, "iid": pipeline_iid, "after": after},
        )
        reports = _reports_from_graphql(data)
        if reports is None:
            return {"count": 0, "nodes": []}
        count = reports.get("count", 0)
        all_nodes.extend(reports.get("nodes") or [])
        page_info = reports.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        after = page_info.get("endCursor")
        if not after:
            break
    return {"count": count, "nodes": all_nodes}


def _reports_from_graphql(data: Any) -> dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    project = data.get("project")
    if not isinstance(project, dict):
        return None
    pipeline = project.get("pipeline")
    if not isinstance(pipeline, dict):
        return None
    reports = pipeline.get("codeQualityReports")
    if not isinstance(reports, dict):
        return None
    return reports


def _fetch_code_quality_reports(
    client: GlabClient,
    ref: str | None,
    pipeline_iid: str | None,
) -> dict[str, Any]:
    resolved_ref = _resolve_ref(ref)
    resolved_iid = _resolve_pipeline_iid(client, resolved_ref, pipeline_iid)
    project_path = _project_path(client)
    reports = _fetch_reports(client, project_path, resolved_iid)
    count = reports.get("count", 0)
    print(
        f"ref={resolved_ref} pipeline_iid={resolved_iid} count={count}",
        file=sys.stderr,
    )
    return {"reports": reports}


def main(
    *,
    ref: str | None = None,
    pipeline_iid: str | None = None,
    glab: GlabClient | None = None,
) -> int:
    def _run() -> int:
        client = glab or default_glab()
        result = _fetch_code_quality_reports(client, ref, pipeline_iid)
        return emit.succeed(COMMAND, result)

    return emit.run_guarded(COMMAND, _run)
