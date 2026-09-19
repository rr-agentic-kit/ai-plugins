from __future__ import annotations

import json
import re
from typing import Any, cast

from errors import GlabError
from gitutil import current_branch, open_mr_iid_for_branch, require_worktree
from glab import GlabClient

MR_URL_IID_RE = re.compile(r"/merge_requests/(\d+)/?$")


def parse_mr_iid(mr_ref: str) -> str:
    ref = mr_ref.strip()
    if ref.startswith("!"):
        return ref[1:]
    if ref.isdigit():
        return ref
    match = MR_URL_IID_RE.search(ref)
    if match:
        return match.group(1)
    raise GlabError(f"could not parse merge request reference: {mr_ref}")


def resolve_open_mr(glab: GlabClient, mr_ref: str | None) -> dict[str, Any]:
    if mr_ref:
        iid = parse_mr_iid(mr_ref)
        mr = glab.api(f"projects/:fullpath/merge_requests/{iid}")
        located = str(mr.get("iid", ""))
        if located != iid:
            raise GlabError(
                f"could not locate merge request !{iid} "
                "(need glab project context: run from repo cwd, or set GITLAB_REPO)"
            )
    else:
        require_worktree()
        glab.cli(["repo", "view", "--output", "json"])
        branch = current_branch()
        iid = open_mr_iid_for_branch(glab, branch)
        mr = glab.api(f"projects/:fullpath/merge_requests/{iid}")

    state = str(mr.get("state", ""))
    resolved_iid = str(mr.get("iid", iid))
    if state != "opened":
        raise GlabError(
            f"merge request !{resolved_iid} is not open (state: {state})"
        )
    return cast(dict[str, Any], mr)


def auth_check(glab: GlabClient) -> None:
    try:
        glab.cli(["auth", "status"])
    except GlabError as exc:
        raise GlabError("glab is not authenticated; run: glab auth login") from exc


def resolve_mr_iid(glab: GlabClient, mr_iid: str | None) -> str:
    if mr_iid:
        mr = glab.api(f"projects/:fullpath/merge_requests/{mr_iid}")
        located = str(mr.get("iid", ""))
        if located != mr_iid:
            raise GlabError(
                f"could not locate merge request !{mr_iid} "
                "(need glab project context: run from repo cwd, or set GITLAB_REPO)"
            )
        return mr_iid
    require_worktree()
    glab.cli(["repo", "view", "--output", "json"])
    branch = current_branch()
    return open_mr_iid_for_branch(glab, branch)


def project_path(glab: GlabClient) -> str:
    raw = glab.cli(["repo", "view", "--output", "json"])
    payload = json.loads(raw)
    path = payload.get("path_with_namespace")
    if not path:
        raise GlabError("could not resolve project path (glab repo view)")
    return str(path)


def current_username(glab: GlabClient) -> str:
    me = glab.api("user")
    username = me.get("username")
    if not username:
        raise GlabError("could not resolve current GitLab user (glab api user)")
    return str(username)
