#!/usr/bin/env python3
"""CI-facing release branch control: open/rc/promote/hotfix/next-minor."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from packaging.version import Version

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import bump_plugins_version as bump  # noqa: E402
from validate_plugin_versions import REPO_ROOT  # noqa: E402

RELEASE_BRANCH = re.compile(r"^release/(?P<version>\d+\.\d+\.\d+)$")
HOTFIX_BRANCH = re.compile(r"^hotfix/(?P<version>\d+\.\d+\.\d+)$")
COMMANDS = ("open", "rc", "promote", "hotfix", "next-minor")


def _emit(**kwargs: object) -> None:
    for key, value in kwargs.items():
        if value is not None:
            print(f"{key}={value}")


def _fail(message: str) -> int:
    print(f"ci_release_control: {message}", file=sys.stderr)
    return 1


def parse_release_branch(branch: str) -> str:
    match = RELEASE_BRANCH.match(branch.strip())
    if not match:
        raise ValueError(f"not a release branch: {branch!r}")
    version = match.group("version")
    parts = version.split(".")
    if int(parts[2]) != 0:
        raise ValueError(
            f"release branch must end in .0 (got {branch!r}); use hotfix/ for patches"
        )
    return version


def parse_hotfix_branch(branch: str) -> str:
    match = HOTFIX_BRANCH.match(branch.strip())
    if not match:
        raise ValueError(f"not a hotfix branch: {branch!r}")
    version = match.group("version")
    if int(version.split(".")[2]) == 0:
        raise ValueError(f"hotfix branch patch must be > 0 (got {branch!r})")
    return version


def next_minor_version(version: str) -> str:
    parsed = Version(version)
    release = parsed.release
    if len(release) < 2:
        raise ValueError(f"cannot compute next minor from {version!r}")
    major, minor = release[0], release[1]
    return f"{major}.{minor + 1}.0"


def branch_from_ref(ref: str | None) -> str:
    if not ref:
        return ""
    ref = ref.strip()
    if ref.startswith("refs/heads/"):
        return ref.removeprefix("refs/heads/")
    return ref


def resolve_branch(args: argparse.Namespace) -> str:
    if args.branch:
        return args.branch.strip()
    for env_name in ("GITHUB_HEAD_REF", "GITHUB_REF_NAME", "GITHUB_REF"):
        raw = os.environ.get(env_name)
        if raw:
            return branch_from_ref(raw)
    raise ValueError("branch required: pass --branch or set GITHUB_HEAD_REF")


def run_open(branch: str, repo_root: Path) -> int:
    base = parse_release_branch(branch)
    target = f"{base}-rc1"
    bump.set_lockstep_version(target, repo_root)
    _emit(action="open", branch=branch, version=target)
    return 0


def run_rc(repo_root: Path) -> int:
    version = bump.run_bump("rc", repo_root)
    _emit(action="rc", version=version)
    return 0


def run_promote(branch: str, repo_root: Path) -> int:
    expected = parse_release_branch(branch)
    version = bump.run_bump("stable", repo_root)
    if version != expected:
        return _fail(
            f"promoted version {version!r} does not match branch base {expected!r}"
        )
    next_version = next_minor_version(version)
    _emit(
        action="promote",
        branch=branch,
        version=version,
        next_version=next_version,
        next_branch=f"release/{next_version}",
    )
    return 0


def run_hotfix(branch: str, repo_root: Path) -> int:
    version = parse_hotfix_branch(branch)
    bump.set_lockstep_version(version, repo_root)
    _emit(action="hotfix", branch=branch, version=version)
    return 0


def run_next_minor(version: str | None, repo_root: Path) -> int:
    if version:
        current = version.strip()
    else:
        from validate_plugin_versions import _read_pyproject_version

        current = _read_pyproject_version(repo_root / "pyproject.toml")
    next_version = next_minor_version(current)
    _emit(
        action="next-minor",
        version=current,
        next_version=next_version,
        next_branch=f"release/{next_version}",
    )
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Release branch version control for CI workflows.",
    )
    parser.add_argument(
        "command",
        choices=COMMANDS,
        help="Release control command",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Branch name (default: GITHUB_HEAD_REF / GITHUB_REF_NAME)",
    )
    parser.add_argument(
        "--version",
        default=None,
        help="Explicit version for next-minor (default: read pyproject.toml)",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=REPO_ROOT,
        help="Repository root (default: script parent directory)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo.resolve()
    try:
        if args.command == "open":
            return run_open(resolve_branch(args), repo_root)
        if args.command == "rc":
            return run_rc(repo_root)
        if args.command == "promote":
            return run_promote(resolve_branch(args), repo_root)
        if args.command == "hotfix":
            return run_hotfix(resolve_branch(args), repo_root)
        if args.command == "next-minor":
            return run_next_minor(args.version, repo_root)
    except ValueError as exc:
        return _fail(str(exc))
    except SystemExit as exc:
        if exc.code not in (0, None):
            return int(exc.code) if isinstance(exc.code, int) else 1
        raise
    return _fail(f"unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
