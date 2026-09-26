#!/usr/bin/env python3
"""Create a work branch off an open release train."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from release_branches import (  # noqa: E402
    GhRunner,
    GitError,
    GitRunner,
    die,
    emit,
    is_reserved_branch_name,
    list_release_branches,
    pick_release_branch,
    require_gh,
)
from validate_plugin_versions import REPO_ROOT  # noqa: E402

PROG = "branch_new"


def usage() -> str:
    return """Create a work branch off an open release train (not hotfix/master).

Usage:
  branch_new.py <branch-name> [--base release/X.Y.0] [--no-push]

Base resolution when --base is omitted:
  1 open release  → use it
  2+ open         → interactive select (or fail if non-TTY)

Flags:
  --base <release/X.Y.0>   Explicit integration base
  --no-push                Do not push -u to origin
  --repo <owner/name>      Override gh/git remote repo for branch listing
  -h, --help"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("--base")
    parser.add_argument("--no-push", action="store_true")
    parser.add_argument("--repo")
    parser.add_argument("name", nargs="?")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv)
    if ns.help:
        print(usage())
        return 0
    if not ns.name:
        print(usage())
        return 2

    name = ns.name
    if is_reserved_branch_name(name):
        die(f"refusing reserved branch name: {name}", prog=PROG)
    if " " in name:
        die("branch name must not contain spaces", prog=PROG)

    repo_root = REPO_ROOT
    gh = GhRunner(ns.repo)
    git = GitRunner()
    require_gh(gh, prog=PROG)

    branches = list_release_branches(gh, git, repo_root)
    base = pick_release_branch(branches, ns.base, prog=PROG)

    git.run(["fetch", "origin", base], cwd=repo_root)
    try:
        git.run(
            ["show-ref", "--verify", "--quiet", f"refs/heads/{name}"], cwd=repo_root
        )
        die(f"local branch already exists: {name}", prog=PROG)
    except GitError:
        pass

    try:
        git.run(["ls-remote", "--exit-code", "--heads", "origin", name], cwd=repo_root)
        die(f"remote branch already exists: origin/{name}", prog=PROG)
    except GitError:
        pass

    git.run(["checkout", "--no-track", "-b", name, f"origin/{base}"], cwd=repo_root)
    emit("status=created", f"branch={name}", f"base={base}")

    if not ns.no_push:
        git.run(["push", "-u", "origin", name], cwd=repo_root)
        emit(f"pushed=origin/{name}")
    else:
        emit("pushed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
