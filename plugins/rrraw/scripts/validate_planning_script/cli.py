"""argparse CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .constants import DOCS_ROOT_NAME, PHASE_DIRS, SCHEMA_PATH, TRACK_DIR_RE
from .models import Issue
from .rewrite import rewrite_planning_dir
from .setup import find_repo_root, run_setup, sync_agent_injection
from .validate import validate_dir
from .workspace import docs_root, has_cascade_docs, phase_root


def require_python() -> None:
    if sys.version_info < (3, 14):  # noqa: UP036
        print(
            "validate_planning: need CPython 3.14+ with PyYAML "
            "(tried uv, python3.14, python3, python). From plugin root: "
            "python3 -m pip install -r "
            "scripts/validate_planning_script/requirements.txt",
            file=sys.stderr,
        )
        raise SystemExit(127)


def _error_count(issues: list[Issue]) -> int:
    return sum(1 for issue in issues if issue.severity == "error")


def _print_issues(issues: list[Issue]) -> int:
    for issue in issues:
        stream = sys.stderr if issue.severity == "error" else sys.stdout
        print(issue.format(), file=stream)
    count = _error_count(issues)
    if count:
        print(f"{count} error(s)", file=sys.stderr)
    return count


def _docs_from_phase(planning_dir: Path, repo: Path) -> Path:
    """Resolve ``docs/`` from a phase dir under version-first or legacy layout."""
    root = phase_root(planning_dir)
    if root.name in PHASE_DIRS:
        parent = root.parent
        if TRACK_DIR_RE.fullmatch(parent.name):
            # docs/rr/{track}/{phase}
            rr = parent.parent
            if rr.name == "rr":
                return rr.parent
        if parent.name == "rr":
            return parent.parent
        return parent
    return docs_root(repo)


def main(argv: list[str] | None = None) -> int:
    require_python()
    parser = argparse.ArgumentParser(
        description=(
            "Validate rr-planner markdown item headers, graph, status, "
            "and items.json drift. --setup bootstraps docs/rr/ framework layout."
        )
    )
    parser.add_argument(
        "planning_dir",
        type=Path,
        nargs="?",
        default=None,
        help=(
            "Phase directory to validate/rewrite "
            "(docs/rr/{track}/discovery or .../plan). "
            "Optional with --setup (framework uses --docs-root)."
        ),
    )
    parser.add_argument(
        "--depth",
        choices=("shallow", "standard", "deep"),
        default="standard",
    )
    parser.add_argument(
        "--format",
        choices=("md", "yaml", "json"),
        default=None,
        dest="doc_format",
        help="Human plan doc extension. yaml and json are rejected "
        "(UNSUPPORTED_FORMAT).",
    )
    parser.add_argument(
        "--rewrite",
        action="store_true",
        help=(
            "Migrate legacy shapes (ES/PRD, challenge-report, frd), "
            "list-meta, and cascade yaml to canonical md."
        ),
    )
    parser.add_argument(
        "--sync-agent-config",
        action="store_true",
        help="Emit docs/rr/agent.plan.md and append the load line to existing "
        "root agent SoT files.",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Bootstrap or repair docs/rr/, versioned phase dirs, "
        "rrr-status.yaml, phase status.yaml files, agent.plan.md, "
        "and cascade frontmatter.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repo root for CLAUDE.md / AGENTS.md sync. Default: git "
        "toplevel from planning_dir or cwd.",
    )
    parser.add_argument(
        "--docs-root",
        type=Path,
        default=None,
        help=f"Docs tree root for --setup / --sync-agent-config. "
        f"Default: {{repo-root}}/{DOCS_ROOT_NAME}.",
    )
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    args = parser.parse_args(argv)
    if args.setup:
        start = args.planning_dir or args.docs_root or Path.cwd()
        repo = args.repo_root or find_repo_root(start)
        docs = (
            docs_root(repo, override=args.docs_root)
            if args.docs_root is not None
            else docs_root(repo)
        )
        if (
            args.planning_dir is not None
            and args.planning_dir.name == "plans"
            and args.docs_root is None
        ):
            print(
                "note\tok\t--setup no longer takes a plans-dir; "
                f"using {docs} (legacy docs/plans/ migrates via layout migrate)",
                flush=True,
            )
        return run_setup(docs, repo)
    if args.planning_dir is None:
        parser.error("planning_dir is required unless --setup")
    if not args.planning_dir.is_dir():
        print(
            f"ERROR [NO_DIR]: {args.planning_dir} is not a directory", file=sys.stderr
        )
        return 1
    if not args.schema.is_file():
        print(f"WARN [SCHEMA_MISSING]: {args.schema} not found", file=sys.stderr)
    if args.sync_agent_config:
        repo = args.repo_root or find_repo_root(args.planning_dir)
        docs = (
            docs_root(repo, override=args.docs_root)
            if args.docs_root is not None
            else _docs_from_phase(args.planning_dir, repo)
        )
        sync_issues = sync_agent_injection(docs, repo, force=True)
        if _print_issues(sync_issues):
            return 1
    if args.rewrite:
        rewrite_issues = rewrite_planning_dir(args.planning_dir)
        if _print_issues(rewrite_issues):
            return 1
    has_cascade = has_cascade_docs(args.planning_dir)
    if args.sync_agent_config and not args.rewrite and not has_cascade:
        print("OK")
        return 0
    issues = validate_dir(
        args.planning_dir, depth=args.depth, doc_format=args.doc_format
    )
    if _print_issues(issues):
        return 1
    print("OK")
    return 0
