"""List SonarQube issues via sonarqube-cli (forge-agnostic)."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode

import emit
from errors import GhError, GitError, GlabError
from forge import detect
from gh import default_gh
from gitutil import current_branch, open_mr_iid_for_branch, repo_root
from glab import default_glab

COMMAND = "sonar-list-issues"
_PROJECT_KEY_RE = re.compile(r"^[a-zA-Z0-9_\-\.:]+$")
_BRANCH_RE = re.compile(r"^[a-zA-Z0-9_\-\./]+$")
_PROPS_NAME = "sonar-project.properties"
_PROPS_GLOB_DEPTH = ("*", "*/*", "*/*/*")


class SonarError(Exception):
    def __init__(self, message: str, *, code: str = "sonar_error") -> None:
        super().__init__(message)
        self.code = code


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        COMMAND,
        help="List SonarQube issues (machine JSON; wrap sonarqube-cli)",
        description=(
            "Result keys: project, total, issues[]; optional pull_request, branch. "
            "With --lean: by_file map (key/rule/severity/line), issues omitted. "
            "Default scope: open PR/MR for current branch"
        ),
    )
    parser.add_argument(
        "-p",
        "--project",
        help="Sonar project key (default: sonar.projectKey in properties)",
    )
    parser.add_argument(
        "--pull-request",
        dest="pull_request",
        help="Pull/merge request id (default: open PR/MR for current branch)",
    )
    parser.add_argument(
        "--branch",
        help="Branch name for Sonar analysis (skips PR auto-detect)",
    )
    parser.add_argument(
        "--statuses",
        default="OPEN,CONFIRMED",
        help="Comma-separated statuses (default: OPEN,CONFIRMED)",
    )
    parser.add_argument(
        "--lean",
        action="store_true",
        help="Group by file; omit full issues[]/messages (for --fix --sonar)",
    )
    parser.set_defaults(handler=_handler)


def _handler(args: argparse.Namespace) -> int:
    return main(
        project=args.project,
        pull_request=args.pull_request,
        branch=args.branch,
        statuses=args.statuses,
        lean=args.lean,
    )


def lean_reshape(result: dict[str, Any]) -> dict[str, Any]:
    """Collapse full issues[] into by_file lean rows (no message dump)."""
    by_file: dict[str, list[dict[str, Any]]] = {}
    for issue in result.get("issues") or []:
        if not isinstance(issue, dict):
            continue
        path = str(issue.get("file") or "")
        row = {
            "key": issue.get("key"),
            "rule": issue.get("rule"),
            "severity": issue.get("severity"),
            "line": issue.get("line"),
        }
        by_file.setdefault(path, []).append(row)
    lean: dict[str, Any] = {
        "project": result.get("project"),
        "total": result.get("total"),
        "by_file": by_file,
    }
    if result.get("pull_request") is not None:
        lean["pull_request"] = result["pull_request"]
    if result.get("branch") is not None:
        lean["branch"] = result["branch"]
    return lean


def _project_key_from_properties(props: Path) -> str | None:
    for line in props.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("sonar.projectKey="):
            key = stripped.split("=", 1)[1].strip()
            if _PROJECT_KEY_RE.fullmatch(key):
                return key
            raise SonarError(
                f"invalid project key in properties: {key!r}", code="invalid_project"
            )
    return None


def _discover_properties_files(root: Path) -> list[Path]:
    found: list[Path] = []
    root_props = root / _PROPS_NAME
    if root_props.is_file():
        found.append(root_props)
    for pattern in _PROPS_GLOB_DEPTH:
        for path in sorted(root.glob(f"{pattern}/{_PROPS_NAME}")):
            if path.is_file() and path not in found:
                found.append(path)
    return found


def _resolve_project_key(explicit: str | None) -> str:
    if explicit:
        key = explicit.strip()
        if not _PROJECT_KEY_RE.fullmatch(key):
            raise SonarError(f"invalid project key: {key!r}", code="invalid_project")
        return key
    root = Path(repo_root())
    candidates: list[tuple[str, str]] = []
    for props in _discover_properties_files(root):
        key = _project_key_from_properties(props)
        if key is None:
            continue
        rel = str(props.relative_to(root))
        candidates.append((rel, key))
    if len(candidates) == 1:
        return candidates[0][1]
    if len(candidates) > 1:
        detail = ", ".join(f"{path}={key}" for path, key in candidates)
        raise SonarError(
            f"multiple sonar.projectKey candidates: {detail}; pass -p/--project",
            code="ambiguous_project",
        )
    raise SonarError(
        "missing -p/--project and no sonar.projectKey in properties "
        f"(searched repo root and depth≤3 */{_PROPS_NAME})",
        code="missing_project",
    )


def _component_file(component: str, project: str) -> str:
    prefix = f"{project}:"
    if component.startswith(prefix):
        return component[len(prefix) :]
    return component


def _normalize_issue(raw: dict[str, Any], project: str) -> dict[str, Any]:
    component = str(raw.get("component") or "")
    return {
        "key": raw.get("key"),
        "rule": raw.get("rule"),
        "severity": raw.get("severity"),
        "type": raw.get("type"),
        "file": _component_file(component, project),
        "line": raw.get("line"),
        "message": raw.get("message"),
        "status": raw.get("status") or raw.get("issueStatus"),
    }


def _open_pr_for_current_branch() -> str:
    """Resolve open PR/MR iid for the current branch (forge via origin)."""
    branch = current_branch()
    remote = detect()
    if remote.forge == "github":
        # `gh pr view` takes branch as positional; `--head` is not a valid flag.
        raw = default_gh().cli(
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
            raise SonarError(
                f"no open pull request for branch: {branch}",
                code="no_open_pr",
            )
        return number
    if remote.forge == "gitlab":
        return open_mr_iid_for_branch(default_glab(), branch)
    raise SonarError(
        "forge unknown for PR auto-scope; pass --pull-request or --branch",
        code="forge_unknown",
    )


def _resolve_scope(
    pull_request: str | None, branch: str | None
) -> tuple[str | None, str | None]:
    if branch and pull_request:
        raise SonarError(
            "pass only one of --branch or --pull-request",
            code="invalid_scope",
        )
    if pull_request is not None:
        if not str(pull_request).isdigit():
            raise SonarError(
                f"invalid pull-request id: {pull_request!r}",
                code="invalid_pull_request",
            )
        return str(pull_request), None
    if branch is not None:
        if not _BRANCH_RE.fullmatch(branch):
            raise SonarError(f"invalid branch: {branch!r}", code="invalid_branch")
        return None, branch
    return _open_pr_for_current_branch(), None


def _parse_issues_payload(stdout: str, project: str) -> tuple[list[dict[str, Any]], int]:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise SonarError(
            f"sonar stdout not JSON: {exc}", code="sonar_parse_error"
        ) from exc

    raw_issues = payload.get("issues") if isinstance(payload, dict) else None
    if not isinstance(raw_issues, list):
        raise SonarError("sonar JSON missing issues[]", code="sonar_parse_error")

    issues = [
        _normalize_issue(item, project) for item in raw_issues if isinstance(item, dict)
    ]
    total = (
        payload.get("paging", {}).get("total") if isinstance(payload, dict) else None
    )
    if not isinstance(total, int):
        total = len(issues)
    return issues, total


def _run_sonar_list(
    *,
    project: str,
    pull_request: str | None,
    branch: str | None,
    statuses: str,
) -> tuple[list[dict[str, Any]], int]:
    cmd = [
        "sonar",
        "list",
        "issues",
        "-p",
        project,
        "--format",
        "json",
        "--statuses",
        statuses,
    ]
    if pull_request:
        cmd.extend(["--pull-request", str(pull_request)])
    if branch:
        cmd.extend(["--branch", branch])

    completed = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = (
            completed.stderr or completed.stdout or ""
        ).strip() or "sonar list issues failed"
        raise SonarError(detail, code="sonar_cli_failed")
    return _parse_issues_payload(completed.stdout, project)


def _run_sonar_api_search(
    *,
    project: str,
    pull_request: str | None,
    branch: str | None,
    statuses: str,
) -> tuple[list[dict[str, Any]], int]:
    """Fallback when `sonar list issues` returns empty but issues exist via API."""
    params: dict[str, str] = {
        "componentKeys": project,
        "ps": "500",
        "statuses": statuses,
    }
    if pull_request:
        params["pullRequest"] = str(pull_request)
    if branch:
        params["branch"] = branch
    endpoint = f"/api/issues/search?{urlencode(params, quote_via=quote)}"
    completed = subprocess.run(
        ["sonar", "api", "get", endpoint],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = (
            completed.stderr or completed.stdout or ""
        ).strip() or "sonar api issues search failed"
        raise SonarError(detail, code="sonar_cli_failed")
    return _parse_issues_payload(completed.stdout, project)


def _run_sonar(
    *,
    project: str,
    pull_request: str | None,
    branch: str | None,
    statuses: str,
) -> dict[str, Any]:
    if shutil.which("sonar") is None:
        raise SonarError(
            "sonarqube-cli (`sonar`) not on PATH — install/auth before --fix --sonar",
            code="sonar_not_found",
        )
    pull_request, branch = _resolve_scope(pull_request, branch)

    issues, total = _run_sonar_list(
        project=project,
        pull_request=pull_request,
        branch=branch,
        statuses=statuses,
    )
    # `sonar list issues` can return total=0 while /api/issues/search still has OPEN
    # findings for the same PR (observed SonarCloud). Fall back once when empty.
    if total == 0 and (pull_request or branch):
        try:
            api_issues, api_total = _run_sonar_api_search(
                project=project,
                pull_request=pull_request,
                branch=branch,
                statuses=statuses,
            )
        except SonarError:
            api_issues, api_total = issues, total
        if api_total > 0:
            issues, total = api_issues, api_total

    result: dict[str, Any] = {
        "project": project,
        "total": total,
        "issues": issues,
    }
    if pull_request:
        result["pull_request"] = str(pull_request)
    if branch:
        result["branch"] = branch
    return result


def main(
    *,
    project: str | None = None,
    pull_request: str | None = None,
    branch: str | None = None,
    statuses: str = "OPEN,CONFIRMED",
    lean: bool = False,
) -> int:
    try:
        key = _resolve_project_key(project)
        result = _run_sonar(
            project=key,
            pull_request=pull_request,
            branch=branch,
            statuses=statuses,
        )
        if lean:
            result = lean_reshape(result)
    except SonarError as exc:
        return emit.fail(COMMAND, exc.code, str(exc))
    except (FileNotFoundError, GitError, GhError, GlabError) as exc:
        return emit.fail_exception(COMMAND, exc)
    return emit.succeed(COMMAND, result)
