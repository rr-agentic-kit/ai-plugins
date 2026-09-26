#!/usr/bin/env python3
"""Open or update a PR into an open release train."""

from __future__ import annotations

import argparse
import json
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
    is_reserved_pr_head,
    list_release_branches,
    pick_release_branch,
    require_gh,
)
from validate_plugin_versions import REPO_ROOT  # noqa: E402

PROG = "create_pr"


def usage() -> str:
    return """Open or update a PR into an open release train (work → release/*).

Usage:
  create_pr.py --title "..." --description "..."
  create_pr.py --title "..." --description "..." --base release/0.1.0
  create_pr.py --title "..." --body-file path.md

Base resolution when --base is omitted: sole open release, else select.
If a PR already exists for the head branch, updates title/body/base (no second PR).

Flags:
  --title <text>             Required
  --description <text>       PR body (alias: --body)
  --body-file <path>         PR body from file (overrides --description)
  --base <release/X.Y.0>     Integration base
  --head <branch>            Head branch (default: current)
  --draft                    Create as draft (ignored on update)
  --repo <owner/name>        Override gh repo
  -h, --help"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("--title")
    parser.add_argument("--description")
    parser.add_argument("--body")
    parser.add_argument("--body-file")
    parser.add_argument("--base")
    parser.add_argument("--head")
    parser.add_argument("--draft", action="store_true")
    parser.add_argument("--repo")
    return parser.parse_args(argv)


def _body_args(ns: argparse.Namespace) -> list[str]:
    title = ns.title
    description = ns.description or ns.body
    body_file = ns.body_file

    if not title:
        die("--title is required", prog=PROG)
    if body_file:
        body_path = Path(body_file)
        if not body_path.is_file():
            die(f"body file not found: {body_file}", prog=PROG)
        return ["--body-file", body_file]
    if not description:
        die("--description or --body-file is required", prog=PROG)
    return ["--body", description]


def _resolve_head(ns: argparse.Namespace, git: GitRunner, repo_root: Path) -> str:
    head = ns.head
    if not head:
        head = git.run(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)
    if is_reserved_pr_head(head):
        die(f"refusing PR head: {head}", prog=PROG)
    return head


def _ensure_remote_head(git: GitRunner, repo_root: Path, head: str) -> None:
    try:
        git.run(
            ["ls-remote", "--exit-code", "--heads", "origin", "--", head],
            cwd=repo_root,
        )
    except GitError:
        git.run(
            ["push", "-u", "origin", "--", f"HEAD:refs/heads/{head}"],
            cwd=repo_root,
        )


def _upsert_pr(
    gh: GhRunner,
    *,
    title: str,
    body_args: list[str],
    base: str,
    head: str,
    draft: bool,
) -> str:
    existing_json = gh.run(["pr", "list", "--head", head, "--json", "url,number"])
    existing = json.loads(existing_json) if existing_json.strip() else []
    existing_url = existing[0]["url"] if existing else ""
    existing_num = str(existing[0]["number"]) if existing else ""

    if existing_num:
        gh.run(
            ["pr", "edit", existing_num, "--title", title, *body_args, "--base", base]
        )
        emit("status=updated", f"url={existing_url}", f"base={base}", f"head={head}")
        print(existing_url)
        return existing_url

    create_args = [
        "pr",
        "create",
        "--title",
        title,
        "--base",
        base,
        "--head",
        head,
        *body_args,
    ]
    if draft:
        create_args.append("--draft")
    url = gh.run(create_args)
    emit("status=created", f"url={url}", f"base={base}", f"head={head}")
    print(url)
    return url


def main(argv: list[str] | None = None) -> None:
    ns = parse_args(argv)
    if ns.help:
        print(usage())
        return

    body_args = _body_args(ns)
    repo_root = REPO_ROOT
    gh = GhRunner(ns.repo)
    git = GitRunner()
    require_gh(gh, prog=PROG)

    head = _resolve_head(ns, git, repo_root)
    branches = list_release_branches(gh, git, repo_root)
    base = pick_release_branch(branches, ns.base, prog=PROG)
    _ensure_remote_head(git, repo_root, head)
    _upsert_pr(
        gh,
        title=ns.title,
        body_args=body_args,
        base=base,
        head=head,
        draft=ns.draft,
    )


if __name__ == "__main__":
    main()
