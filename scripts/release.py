#!/usr/bin/env python3
"""Maintainer front-end for .github/workflows/release-control.yml."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from release_branches import (  # noqa: E402
    WORKFLOW,
    GhError,
    GhRunner,
    GitError,
    GitRunner,
    default_branch,
    die,
    emit,
    has_workflow_at,
    list_release_branches,
    lowest_open_release,
    require_gh,
    sorted_release_branches,
    validate_hotfix_branch_name,
    validate_release_branch_name,
    workflow_ref_for,
)
from validate_plugin_versions import REPO_ROOT  # noqa: E402

PROG = "release"


def usage() -> str:
    return """Maintainer front-end for .github/workflows/release-control.yml.
Dispatches via gh; does not bump versions locally (CI owns that).

Usage:
  release.py <command> [args] [flags]

Commands:
  open [release/X.Y.0]     Set train to X.Y.0-rc1 (default: lowest open release/*)
  rc [release/X.Y.0]       Tick RC (default: lowest open release/*)
  promote [release/X.Y.0]  Graduate train (default: lowest open release/*)
  hotfix <hotfix/X.Y.Z>    Ship patch version from hotfix branch name
  next-minor [VERSION]     Print next minor train (CI helper; optional version)
  seed <X.Y.0>             Create+push release/X.Y.0 from master, then open
  active                   Print the lowest open release/* branch
  watch                    Watch the latest release-control run
  status                   Active release/* branches + recent workflow runs

When a release branch is omitted, the script picks the lowest semver among
remote heads matching release/N.N.0 (e.g. release/0.1.0 before release/0.2.0).

Flags:
  --ref <branch>           Branch whose workflow YAML to run
  --repo <owner/name>      Override gh repo (default: cwd origin)
  --yes                    Skip seed confirmation
  -h, --help               Show this help"""


def resolve_branch_arg(kind: str, branch: str | None, branches: list[str]) -> str:
    if not branch:
        if kind == "release":
            return lowest_open_release(branches, prog=PROG)
        die("hotfix branch required (e.g. hotfix/0.1.1)", prog=PROG)
    if kind == "release":
        validate_release_branch_name(branch, prog=PROG)
    else:
        validate_hotfix_branch_name(branch, prog=PROG)
    return branch


def dispatch(
    gh: GhRunner,
    git: GitRunner,
    *,
    repo_root: Path,
    branches: list[str],
    action: str,
    branch: str | None = None,
    version: str | None = None,
    ref_override: str | None,
    default_branch_name: str,
) -> None:
    run_ref = workflow_ref_for(
        git,
        branches,
        repo_root=repo_root,
        ref_override=ref_override,
        target=branch,
        default_branch_name=default_branch_name,
        prog=PROG,
    )
    args = ["workflow", "run", WORKFLOW, "--ref", run_ref, "-f", f"action={action}"]
    if branch:
        args.extend(["-f", f"branch={branch}"])
    if version:
        args.extend(["-f", f"version={version}"])
    gh.run(args)
    emit("status=dispatched", f"action={action}")
    if branch:
        emit(f"branch={branch}")
    if version:
        emit(f"version={version}")
    emit(f"ref={run_ref}")
    emit("hint=run: just release watch")


def cmd_open(
    gh: GhRunner,
    git: GitRunner,
    *,
    repo_root: Path,
    branches: list[str],
    branch_arg: str | None,
    ref_override: str | None,
    default_branch_name: str,
) -> None:
    branch = resolve_branch_arg("release", branch_arg, branches)
    dispatch(
        gh,
        git,
        repo_root=repo_root,
        branches=branches,
        action="open",
        branch=branch,
        ref_override=ref_override,
        default_branch_name=default_branch_name,
    )


def cmd_rc(
    gh: GhRunner,
    git: GitRunner,
    *,
    repo_root: Path,
    branches: list[str],
    branch_arg: str | None,
    ref_override: str | None,
    default_branch_name: str,
) -> None:
    branch = resolve_branch_arg("release", branch_arg, branches)
    dispatch(
        gh,
        git,
        repo_root=repo_root,
        branches=branches,
        action="rc",
        branch=branch,
        ref_override=ref_override,
        default_branch_name=default_branch_name,
    )


def cmd_promote(
    gh: GhRunner,
    git: GitRunner,
    *,
    repo_root: Path,
    branches: list[str],
    branch_arg: str | None,
    ref_override: str | None,
    default_branch_name: str,
) -> None:
    branch = resolve_branch_arg("release", branch_arg, branches)
    dispatch(
        gh,
        git,
        repo_root=repo_root,
        branches=branches,
        action="promote",
        branch=branch,
        ref_override=ref_override,
        default_branch_name=default_branch_name,
    )


def cmd_hotfix(
    gh: GhRunner,
    git: GitRunner,
    *,
    repo_root: Path,
    branches: list[str],
    branch_arg: str | None,
    ref_override: str | None,
    default_branch_name: str,
) -> None:
    branch = resolve_branch_arg("hotfix", branch_arg, branches)
    dispatch(
        gh,
        git,
        repo_root=repo_root,
        branches=branches,
        action="hotfix",
        branch=branch,
        ref_override=ref_override,
        default_branch_name=default_branch_name,
    )


def cmd_next_minor(
    gh: GhRunner,
    git: GitRunner,
    *,
    repo_root: Path,
    branches: list[str],
    version: str | None,
    ref_override: str | None,
    default_branch_name: str,
) -> None:
    dispatch(
        gh,
        git,
        repo_root=repo_root,
        branches=branches,
        action="next-minor",
        version=version,
        ref_override=ref_override,
        default_branch_name=default_branch_name,
    )


def cmd_seed(
    gh: GhRunner,
    git: GitRunner,
    *,
    repo_root: Path,
    branches: list[str],
    version: str | None,
    ref_override: str | None,
    default_branch_name: str,
    yes: bool,
    input_fn,
) -> None:
    if not version:
        die("usage: release.py seed <X.Y.0>", prog=PROG)
    from release_branches import SEED_VERSION_PATTERN

    if not SEED_VERSION_PATTERN.fullmatch(version):
        die(f"seed version must be N.N.0, got: {version}", prog=PROG)

    branch = f"release/{version}"
    try:
        gh.run(["api", f"repos/{{owner}}/{{repo}}/branches/{branch}", "--silent"])
        die(f"branch already exists on remote: {branch}", prog=PROG)
    except GhError:
        pass

    if not yes:
        prompt = (
            f"Create and push {branch} from origin/{default_branch_name}, "
            "then dispatch open? [y/N] "
        )
        answer = input_fn(prompt)
        if answer.lower() not in {"y", "yes"}:
            die("aborted", prog=PROG)

    git.run(["fetch", "origin", default_branch_name], cwd=repo_root)
    try:
        git.run(["branch", branch, f"origin/{default_branch_name}"], cwd=repo_root)
    except GitError:
        git.run(
            ["branch", "-f", branch, f"origin/{default_branch_name}"], cwd=repo_root
        )
    git.run(["push", "-u", "origin", branch], cwd=repo_root)

    effective_ref = ref_override
    if not effective_ref and has_workflow_at(git, repo_root, f"origin/{branch}"):
        effective_ref = branch

    dispatch(
        gh,
        git,
        repo_root=repo_root,
        branches=branches,
        action="open",
        branch=branch,
        ref_override=effective_ref,
        default_branch_name=default_branch_name,
    )
    emit(f"seeded={branch}", f"from={default_branch_name}")


def cmd_watch(gh: GhRunner) -> None:
    run_id = gh.run(
        [
            "run",
            "list",
            "--workflow",
            WORKFLOW,
            "--limit",
            "1",
            "--json",
            "databaseId",
            "--jq",
            ".[0].databaseId // empty",
        ]
    )
    if not run_id.strip():
        die("no release-control runs found", prog=PROG)
    emit(f"run_id={run_id.strip()}")
    gh.run(["run", "watch", run_id.strip(), "--exit-status"])


def cmd_active(branches: list[str]) -> None:
    emit(f"branch={lowest_open_release(branches, prog=PROG)}")


def cmd_status(gh: GhRunner, branches: list[str]) -> None:
    emit("=== active release branches ===")
    ordered = sorted_release_branches(branches)
    for branch in ordered:
        emit(branch)
    if ordered:
        emit(f"lowest={ordered[0]}")
    emit("")
    emit("=== recent release-control runs ===")
    print(gh.run(["run", "list", "--workflow", WORKFLOW, "--limit", "8"]))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("--ref")
    parser.add_argument("--repo")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("command", nargs="?")
    parser.add_argument("args", nargs="*")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv)
    if ns.help or not ns.command:
        print(usage())
        return 0 if ns.help else 2

    repo_root = REPO_ROOT
    gh = GhRunner(ns.repo)
    git = GitRunner()
    require_gh(gh, prog=PROG)

    branches = list_release_branches(gh, git, repo_root)
    default_branch_name = default_branch(gh)
    ref_override = ns.ref
    cmd = ns.command
    cmd_args = ns.args

    handlers = {
        "open": lambda: cmd_open(
            gh,
            git,
            repo_root=repo_root,
            branches=branches,
            branch_arg=cmd_args[0] if cmd_args else None,
            ref_override=ref_override,
            default_branch_name=default_branch_name,
        ),
        "rc": lambda: cmd_rc(
            gh,
            git,
            repo_root=repo_root,
            branches=branches,
            branch_arg=cmd_args[0] if cmd_args else None,
            ref_override=ref_override,
            default_branch_name=default_branch_name,
        ),
        "promote": lambda: cmd_promote(
            gh,
            git,
            repo_root=repo_root,
            branches=branches,
            branch_arg=cmd_args[0] if cmd_args else None,
            ref_override=ref_override,
            default_branch_name=default_branch_name,
        ),
        "hotfix": lambda: cmd_hotfix(
            gh,
            git,
            repo_root=repo_root,
            branches=branches,
            branch_arg=cmd_args[0] if cmd_args else None,
            ref_override=ref_override,
            default_branch_name=default_branch_name,
        ),
        "next-minor": lambda: cmd_next_minor(
            gh,
            git,
            repo_root=repo_root,
            branches=branches,
            version=cmd_args[0] if cmd_args else None,
            ref_override=ref_override,
            default_branch_name=default_branch_name,
        ),
        "seed": lambda: cmd_seed(
            gh,
            git,
            repo_root=repo_root,
            branches=branches,
            version=cmd_args[0] if cmd_args else None,
            ref_override=ref_override,
            default_branch_name=default_branch_name,
            yes=ns.yes,
            input_fn=input,
        ),
        "active": lambda: cmd_active(branches),
        "watch": lambda: cmd_watch(gh),
        "status": lambda: cmd_status(gh, branches),
    }

    handler = handlers.get(cmd)
    if handler is None:
        die(f"unknown command: {cmd} (see --help)", prog=PROG)
    handler()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
