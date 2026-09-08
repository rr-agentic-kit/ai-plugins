from __future__ import annotations

import subprocess
from typing import Any
from urllib.parse import quote

from errors import GitError
from glab import GLAB_SINGLE_PAGE, GlabClient

DEFAULT_LOCAL_BRANCHES = ("master", "main")
DEFAULT_INTEGRATION_BRANCHES = ("origin/master", "origin/main")
CHERRY_SAMPLE_LOG_LINES = 3
OPEN_MR_QUERY = (
    "projects/:fullpath/merge_requests?source_branch={encoded}"
    f"&state=opened&per_page={GLAB_SINGLE_PAGE}"
)


def require_worktree() -> None:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise GitError("not a git repository")


def current_branch() -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=False,
    )
    branch = result.stdout.strip()
    if result.returncode != 0 or not branch:
        raise GitError("could not determine current branch")
    return branch


def repo_root() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise GitError("not a git repository")
    return result.stdout.strip()


def opened_mrs_for_branch(glab: GlabClient, branch: str) -> list[Any]:
    encoded = quote(branch, safe="")
    mrs = glab.api(OPEN_MR_QUERY.format(encoded=encoded))
    return mrs if isinstance(mrs, list) else []


def open_mr_iid_for_branch(glab: GlabClient, branch: str) -> str:
    mrs = opened_mrs_for_branch(glab, branch)
    if not mrs:
        raise GitError(f"no open merge request found for branch: {branch}")
    iid = mrs[0].get("iid")
    if iid is None:
        raise GitError(f"no open merge request found for branch: {branch}")
    return str(iid)


def run_git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args], capture_output=True, text=True, check=check
        )
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() if exc.stderr else f"git {' '.join(args)} failed"
        raise GitError(detail) from exc


def upstream_abbrev_ref() -> str | None:
    result = run_git(["rev-parse", "--abbrev-ref", "@{upstream}"], check=False)
    if result.returncode != 0:
        return None
    upstream = result.stdout.strip()
    return upstream or None


def git_output(args: list[str]) -> str:
    result = run_git(args, check=False)
    if result.returncode != 0:
        raise GitError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def staged_hint() -> str:
    staged = run_git(["diff", "--cached", "--quiet"], check=False).returncode != 0
    unstaged = run_git(["diff", "--quiet"], check=False).returncode != 0
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        check=False,
    )
    has_untracked = bool(untracked.stdout.strip())
    if not staged and (unstaged or has_untracked):
        return "all_unstaged"
    if staged and not unstaged and not has_untracked:
        return "all_staged"
    return "partial"


def has_uncommitted_changes() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    return bool(result.stdout.strip())


def resolve_integration_base() -> str:
    run_git(["fetch", "origin"], check=False)
    for candidate in DEFAULT_INTEGRATION_BRANCHES:
        if (
            run_git(["rev-parse", "--verify", "-q", candidate], check=False).returncode
            == 0
        ):
            return candidate
    raise GitError("neither origin/master nor origin/main exists after fetch")


def fetch_remote_branches(remote: str, *branches: str) -> None:
    if not branches:
        return
    run_git(["fetch", remote, *branches])


def remote_ref(remote: str, branch: str) -> str:
    ref = f"{remote}/{branch}"
    if run_git(["rev-parse", "--verify", "-q", ref], check=False).returncode != 0:
        raise GitError(f"remote ref does not exist: {ref}")
    return ref


def merge_base_refs(left: str, right: str) -> str:
    return git_output(["merge-base", left, right])


def diff_name_only(base_sha: str, head_ref: str) -> list[str]:
    out = git_output(["diff", "--name-only", f"{base_sha}..{head_ref}"])
    return [path for path in out.splitlines() if path.strip()]


def already_merged(integration_base: str) -> tuple[bool, str]:
    if (
        run_git(
            ["merge-base", "--is-ancestor", "HEAD", integration_base], check=False
        ).returncode
        == 0
    ):
        return True, f"ancestor: HEAD is ancestor of {integration_base}"
    range_count = git_output(["rev-list", "--count", f"{integration_base}..HEAD"])
    if int(range_count) <= 0:
        return False, ""
    cherry = run_git(["cherry", integration_base, "HEAD"], check=False).stdout
    if cherry.strip():
        non_equiv = sum(1 for line in cherry.splitlines() if line.startswith("+"))
        if non_equiv == 0:
            sample = run_git(
                ["log", "--oneline", f"{integration_base}..HEAD"], check=False
            ).stdout
            sample_line = ";".join(sample.splitlines()[:CHERRY_SAMPLE_LOG_LINES])
            return True, f"all-cherry-equivalent: sample={sample_line}"
    return False, ""
