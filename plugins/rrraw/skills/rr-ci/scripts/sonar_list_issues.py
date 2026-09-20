"""List SonarQube issues via sonarqube-cli (forge-agnostic)."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import emit
from errors import GhError, GitError, GlabError
from forge import detect
from gh import default_gh
from gitutil import current_branch, open_mr_iid_for_branch, repo_root
from glab import default_glab

COMMAND = "sonar-list-issues"
_PROJECT_KEY_RE = re.compile(r"^[a-zA-Z0-9_\-\.:]+$")
_BRANCH_RE = re.compile(r"^[a-zA-Z0-9_\-\./]+$")


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
    parser.set_defaults(handler=_handler)


def _handler(args: argparse.Namespace) -> int:
    return main(
        project=args.project,
        pull_request=args.pull_request,
        branch=args.branch,
        statuses=args.statuses,
    )


def _resolve_project_key(explicit: str | None) -> str:
    if explicit:
        key = explicit.strip()
        if not _PROJECT_KEY_RE.fullmatch(key):
            raise SonarError(f"invalid project key: {key!r}", code="invalid_project")
        return key
    props = Path(repo_root()) / "sonar-project.properties"
    if not props.is_file():
        raise SonarError(
            "missing -p/--project and no sonar.projectKey in properties",
            code="missing_project",
        )
    for line in props.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("sonar.projectKey="):
            key = stripped.split("=", 1)[1].strip()
            if _PROJECT_KEY_RE.fullmatch(key):
                return key
            raise SonarError(
                f"invalid project key in properties: {key!r}", code="invalid_project"
            )
    raise SonarError(
        "sonar-project.properties has no sonar.projectKey",
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
        raw = default_gh().cli(
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

    try:
        payload = json.loads(completed.stdout)
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
) -> int:
    try:
        key = _resolve_project_key(project)
        result = _run_sonar(
            project=key,
            pull_request=pull_request,
            branch=branch,
            statuses=statuses,
        )
    except SonarError as exc:
        return emit.fail(COMMAND, exc.code, str(exc))
    except (FileNotFoundError, GitError, GhError, GlabError) as exc:
        return emit.fail_exception(COMMAND, exc)
    return emit.succeed(COMMAND, result)
