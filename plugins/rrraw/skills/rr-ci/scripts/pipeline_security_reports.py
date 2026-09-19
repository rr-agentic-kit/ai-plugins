from __future__ import annotations

import argparse
import sys
from typing import Any

import emit
from errors import GlabError
from glab import GLAB_LIST_PAGE_SIZE, GLAB_SINGLE_PAGE, GlabClient, default_glab
from mr_common import project_path as _project_path
from mr_common import resolve_mr_iid as _resolve_mr_iid

COMMAND = "pipeline-security-reports"

BLOCKING_SEVERITIES = frozenset({"CRITICAL", "HIGH"})
BLOCKING_STATES = frozenset({"DETECTED", "CONFIRMED"})

_SECURITY_QUERY = f"""
query($fullPath: ID!, $iid: ID!, $after: String) {{
  project(fullPath: $fullPath) {{
    pipeline(iid: $iid) {{
      securityReportFindings(
        severity: [CRITICAL, HIGH, MEDIUM, LOW, INFO, UNKNOWN]
        sort: severity_desc
        first: {GLAB_LIST_PAGE_SIZE}
        after: $after
      ) {{
        count
        nodes {{
          uuid
          title
          severity
          state
          reportType
          falsePositive
          dismissedAt
          dismissalReason
          scanner {{ name vendor }}
          location {{
            ... on VulnerabilityLocationSast {{
              file
              startLine
              endLine
              blobPath
            }}
            ... on VulnerabilityLocationDependencyScanning {{
              file
              blobPath
            }}
          }}
          solution
        }}
        pageInfo {{ endCursor hasNextPage }}
      }}
    }}
  }}
}}"""


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        COMMAND,
        help="Fetch pipeline security tab findings for an MR pipeline",
        description=(
            "Result keys: status, findings (count, nodes, blocking_count, "
            "blocking_nodes), merge_blocked"
        ),
    )
    parser.add_argument("mr_iid", nargs="?", help="Merge request IID")
    parser.add_argument(
        "pipeline_iid", nargs="?", help="Pipeline IID (default: latest for MR)"
    )
    parser.set_defaults(handler=_handler)


def _handler(args: argparse.Namespace) -> int:
    return main(mr_iid=args.mr_iid, pipeline_iid=args.pipeline_iid)


def _resolve_pipeline_iid(
    glab: GlabClient, mr_iid: str, pipeline_iid: str | None
) -> str:
    if pipeline_iid:
        return pipeline_iid
    pipelines = glab.api(
        f"projects/:fullpath/merge_requests/{mr_iid}/pipelines?per_page={GLAB_SINGLE_PAGE}"
    )
    if isinstance(pipelines, list) and pipelines:
        iid = pipelines[0].get("iid")
        if iid is not None:
            return str(iid)
    raise GlabError(f"no pipeline found for merge request !{mr_iid}")


def _findings_from_graphql(data: Any) -> dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    project = data.get("project")
    if not isinstance(project, dict):
        return None
    pipeline = project.get("pipeline")
    if not isinstance(pipeline, dict):
        return None
    findings = pipeline.get("securityReportFindings")
    if not isinstance(findings, dict):
        return None
    return findings


def _fetch_findings(
    glab: GlabClient, project_path: str, pipeline_iid: str
) -> dict[str, Any]:
    all_nodes: list[dict[str, Any]] = []
    after: str | None = None
    count = 0
    while True:
        data = glab.graphql(
            _SECURITY_QUERY,
            variables={"fullPath": project_path, "iid": pipeline_iid, "after": after},
        )
        findings = _findings_from_graphql(data)
        if findings is None:
            return {"count": 0, "nodes": [], "blocking_count": 0, "blocking_nodes": []}
        count = findings.get("count", 0)
        nodes = findings.get("nodes") or []
        all_nodes.extend(nodes)
        page_info = findings.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        after = page_info.get("endCursor")
        if not after:
            break
    blocking_nodes = [node for node in all_nodes if is_blocking(node)]
    return {
        "count": count,
        "nodes": all_nodes,
        "blocking_count": len(blocking_nodes),
        "blocking_nodes": blocking_nodes,
    }


def is_blocking(node: dict[str, Any]) -> bool:
    severity = str(node.get("severity", "")).upper()
    state = str(node.get("state", "")).upper()
    return (
        severity in BLOCKING_SEVERITIES
        and state in BLOCKING_STATES
        and not node.get("falsePositive")
    )


def _resolve_status(findings: dict[str, Any], *, pipeline_found: bool) -> str:
    if not pipeline_found:
        return "no_pipeline"
    if findings.get("count", 0) == 0:
        return "no_reports"
    if findings.get("blocking_count", 0) > 0:
        return "blocking_findings"
    return "clean"


def _fetch_pipeline_security_reports(
    client: GlabClient,
    mr_iid: str | None,
    pipeline_iid: str | None,
) -> dict[str, Any]:
    resolved_mr_iid = _resolve_mr_iid(client, mr_iid)
    resolved_pipeline_iid = _resolve_pipeline_iid(
        client, resolved_mr_iid, pipeline_iid
    )
    project = _project_path(client)
    findings = _fetch_findings(client, project, resolved_pipeline_iid)
    merge_blocked = findings.get("blocking_count", 0) > 0
    status = _resolve_status(findings, pipeline_found=True)
    print(
        f"mr_iid={resolved_mr_iid} pipeline_iid={resolved_pipeline_iid} "
        f"count={findings.get('count', 0)} blocking={findings.get('blocking_count', 0)}",
        file=sys.stderr,
    )
    return {
        "status": status,
        "findings": findings,
        "merge_blocked": merge_blocked,
    }


def main(
    *,
    mr_iid: str | None = None,
    pipeline_iid: str | None = None,
    glab: GlabClient | None = None,
) -> int:
    def _run() -> int:
        client = glab or default_glab()
        result = _fetch_pipeline_security_reports(client, mr_iid, pipeline_iid)
        return emit.succeed(COMMAND, result)

    return emit.run_guarded(COMMAND, _run)
