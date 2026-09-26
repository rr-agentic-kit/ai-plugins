#!/usr/bin/env python3
"""Shared release branch discovery, validation, and subprocess ports."""

from __future__ import annotations

import contextlib
import re
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from packaging.version import Version

from ci_release_control import parse_hotfix_branch, parse_release_branch

RELEASE_PREFIX = "release/"
HOTFIX_PREFIX = "hotfix/"

RELEASE_HEAD_PATTERN = re.compile(rf"^{re.escape(RELEASE_PREFIX)}\d+\.\d+\.0$")
SEED_VERSION_PATTERN = re.compile(r"^\d+\.\d+\.0$")
RELEASE_VERSION_PATTERN = re.compile(r"^\d+\.\d+\.0$")
HOTFIX_VERSION_PATTERN = re.compile(r"^\d+\.\d+\.[1-9]\d*$")

RESERVED_BRANCH_NAMES = frozenset({"master", "main"})
RESERVED_BRANCH_PREFIXES = (RELEASE_PREFIX, HOTFIX_PREFIX)
RESERVED_PR_HEADS = frozenset({"HEAD", "master", "main"})

WORKFLOW = "release-control.yml"


class GhError(RuntimeError):
    """``gh`` subprocess failed."""


class GitError(RuntimeError):
    """``git`` subprocess failed."""


def die(message: str, *, prog: str = "release_branches", code: int = 1) -> None:
    print(f"{prog}: {message}", file=sys.stderr)
    raise SystemExit(code)


def emit(*lines: str) -> None:
    for line in lines:
        print(line)


def validate_release_branch_name(
    branch: str, *, prog: str = "release_branches"
) -> None:
    if not branch.startswith(RELEASE_PREFIX):
        die(f"expected release/X.Y.0, got: {branch}", prog=prog)
    ver = branch.removeprefix(RELEASE_PREFIX)
    if not RELEASE_VERSION_PATTERN.fullmatch(ver):
        die(f"release branch must be N.N.0, got: {branch}", prog=prog)


def validate_hotfix_branch_name(branch: str, *, prog: str = "release_branches") -> None:
    if not branch.startswith(HOTFIX_PREFIX):
        die(f"expected hotfix/X.Y.Z, got: {branch}", prog=prog)
    ver = branch.removeprefix(HOTFIX_PREFIX)
    if not HOTFIX_VERSION_PATTERN.fullmatch(ver):
        die(f"hotfix patch must be > 0, got: {branch}", prog=prog)


def parse_release_version(branch: str) -> str:
    try:
        return parse_release_branch(branch)
    except ValueError as exc:
        message = str(exc)
        if "not a release branch" in message:
            die(f"expected release/X.Y.0, got: {branch}")
        if "must end in .0" in message:
            die(f"release branch must be N.N.0, got: {branch}")
        die(message)


def parse_hotfix_version(branch: str) -> str:
    try:
        return parse_hotfix_branch(branch)
    except ValueError as exc:
        message = str(exc)
        if "not a hotfix branch" in message:
            die(f"expected hotfix/X.Y.Z, got: {branch}")
        if "patch must be > 0" in message:
            die(f"hotfix patch must be > 0, got: {branch}")
        die(message)


def sorted_release_branches(branches: Sequence[str]) -> list[str]:
    release_only = [name for name in branches if RELEASE_HEAD_PATTERN.match(name)]
    return sorted(
        release_only, key=lambda name: Version(name.removeprefix(RELEASE_PREFIX))
    )


def lowest_open_release(
    branches: Sequence[str], *, prog: str = "release_branches"
) -> str:
    ordered = sorted_release_branches(branches)
    if not ordered:
        die("no open release/N.N.0 branches on remote", prog=prog)
    return ordered[0]


def pick_release_branch(
    branches: Sequence[str],
    explicit: str | None = None,
    *,
    input_fn: Callable[[str], str] = input,
    is_tty: bool | None = None,
    prog: str = "release_branches",
) -> str:
    if explicit:
        validate_release_branch_name(explicit, prog=prog)
        return explicit

    ordered = sorted_release_branches(branches)
    if not ordered:
        die("no open release/N.N.0 branches on remote", prog=prog)
    if len(ordered) == 1:
        return ordered[0]

    tty = is_tty if is_tty is not None else sys.stdin.isatty()
    if not tty:
        open_list = " ".join(ordered)
        die(
            "multiple release branches open; pass --base <release/X.Y.0> "
            f"(non-interactive). open: {open_list}",
            prog=prog,
        )

    print("Multiple release trains open. Select base:", file=sys.stderr)
    for index, branch in enumerate(ordered, start=1):
        print(f"  {index}) {branch}", file=sys.stderr)

    while True:
        choice = input_fn(f"Choice [1-{len(ordered)}]: ")
        if choice.isdigit():
            picked = int(choice)
            if 1 <= picked <= len(ordered):
                return ordered[picked - 1]
        print("Invalid choice.", file=sys.stderr)


def is_reserved_branch_name(name: str) -> bool:
    if name in RESERVED_BRANCH_NAMES:
        return True
    return any(name.startswith(prefix) for prefix in RESERVED_BRANCH_PREFIXES)


def is_reserved_pr_head(head: str) -> bool:
    if head in RESERVED_PR_HEADS:
        return True
    return any(head.startswith(prefix) for prefix in RESERVED_BRANCH_PREFIXES)


class GhRunner:
    def __init__(self, repo: str | None = None) -> None:
        self._default_repo = repo

    def run(self, args: Sequence[str], *, repo: str | None = None) -> str:
        cmd = ["gh"]
        effective_repo = repo if repo is not None else self._default_repo
        if effective_repo:
            cmd.extend(["--repo", effective_repo])
        cmd.extend(args)
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            raise GhError(detail or f"gh exited {result.returncode}")
        return result.stdout.rstrip("\n")


_ALLOWED_GIT_SUBCOMMANDS = frozenset(
    {
        "branch",
        "cat-file",
        "checkout",
        "fetch",
        "ls-remote",
        "push",
        "rev-parse",
        "show-ref",
    }
)


def _validate_git_arg(arg: str) -> str:
    if not arg or "\x00" in arg or "\n" in arg or "\r" in arg:
        raise GitError(f"unsafe git argument: {arg!r}")
    return arg


class GitRunner:
    def run(self, args: Sequence[str], *, cwd: Path) -> str:
        if not args:
            raise GitError("empty git argv")
        subcommand = args[0]
        if subcommand not in _ALLOWED_GIT_SUBCOMMANDS:
            raise GitError(f"disallowed git subcommand: {subcommand!r}")
        safe_args = [_validate_git_arg(arg) for arg in args]
        git_bin = shutil.which("git")
        if git_bin is None:
            raise GitError("git not found on PATH")
        cmd = [git_bin, "-C", str(cwd), *safe_args]
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False, shell=False
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            raise GitError(detail or f"git exited {result.returncode}")
        return result.stdout.rstrip("\n")


def require_gh(gh: GhRunner, *, prog: str = "release") -> None:
    if not shutil.which("gh"):
        die("gh not found on PATH", prog=prog)
    try:
        gh.run(["auth", "status", "-h", "github.com"])
    except GhError:
        die("gh not authenticated (gh auth login)", prog=prog)


def list_release_branches(
    gh: GhRunner,
    git: GitRunner,
    repo_root: Path,
) -> list[str]:
    try:
        output = gh.run(
            [
                "api",
                "repos/{owner}/{repo}/branches",
                "--paginate",
                "--jq",
                r'.[] | select(.name | test("^release/[0-9]+\\.[0-9]+\\.0$")) | .name',
            ]
        )
        names = [line for line in output.splitlines() if line.strip()]
        if names:
            return names
    except GhError:
        pass

    try:
        output = git.run(["ls-remote", "--heads", "origin", "release/*"], cwd=repo_root)
    except GitError:
        return []

    names: list[str] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        ref = line.split()[-1].removeprefix("refs/heads/")
        if RELEASE_HEAD_PATTERN.match(ref):
            names.append(ref)
    return names


def default_branch(gh: GhRunner) -> str:
    try:
        name = gh.run(
            [
                "repo",
                "view",
                "--json",
                "defaultBranchRef",
                "--jq",
                ".defaultBranchRef.name",
            ]
        )
        if name.strip():
            return name.strip()
    except GhError:
        pass
    return "master"


def fetch_optional(git: GitRunner, repo_root: Path, ref: str) -> None:
    with contextlib.suppress(GitError):
        git.run(["fetch", "origin", ref], cwd=repo_root)


def has_workflow_at(
    git: GitRunner, repo_root: Path, rev: str, workflow: str = WORKFLOW
) -> bool:
    try:
        git.run(
            ["cat-file", "-e", f"{rev}:.github/workflows/{workflow}"], cwd=repo_root
        )
        return True
    except GitError:
        return False


def workflow_ref_for(
    git: GitRunner,
    branches: Sequence[str],
    *,
    repo_root: Path,
    ref_override: str | None,
    target: str | None,
    default_branch_name: str,
    prog: str = "release",
) -> str:
    if ref_override:
        return ref_override

    fetch_optional(git, repo_root, default_branch_name)
    if has_workflow_at(git, repo_root, f"origin/{default_branch_name}"):
        return default_branch_name

    if target:
        fetch_optional(git, repo_root, target)
        if has_workflow_at(git, repo_root, f"origin/{target}"):
            return target

    lowest = lowest_open_release(branches, prog=prog)
    fetch_optional(git, repo_root, lowest)
    if has_workflow_at(git, repo_root, f"origin/{lowest}"):
        return lowest

    die(f"no branch has .github/workflows/{WORKFLOW}; pass --ref <branch>", prog=prog)
    raise AssertionError("unreachable")
