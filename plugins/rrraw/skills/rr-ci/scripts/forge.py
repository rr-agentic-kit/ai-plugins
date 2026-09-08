from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from errors import GitError
from gitutil import run_git

_GITHUB = re.compile(
    r"(?:github\.com[:/])(?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
    re.I,
)
_GITLAB = re.compile(
    r"(?:gitlab[^:/]*[:/])(?P<owner>.+)/(?P<repo>[^/.]+)(?:\.git)?$",
    re.I,
)


@dataclass(frozen=True)
class Remote:
    forge: str
    host: str
    owner: str
    repo: str


def origin_url() -> str:
    result = run_git(["remote", "get-url", "origin"], check=False)
    if result.returncode != 0:
        raise GitError("no origin remote")
    return result.stdout.strip()


def parse_remote_url(url: str) -> Remote:
    normalized = url.strip()
    if normalized.startswith("git@"):
        # git@host:path
        host_path = normalized.split("@", 1)[1]
        host, _, path = host_path.partition(":")
        https_like = f"https://{host}/{path}"
    else:
        https_like = normalized
    parsed = urlparse(https_like)
    host = (parsed.hostname or "").lower()
    path = (parsed.path or "").lstrip("/")
    gh = _GITHUB.search(normalized) or _GITHUB.search(https_like)
    if ("github.com" in host or gh) and gh:
        return Remote("github", host or "github.com", gh.group("owner"), gh.group("repo"))
    gl = _GITLAB.search(normalized) or _GITLAB.search(https_like)
    if "gitlab" in host or gl:
        if gl:
            return Remote("gitlab", host or "gitlab.com", gl.group("owner"), gl.group("repo"))
        parts = path.removesuffix(".git").split("/")
        if len(parts) >= 2:
            return Remote("gitlab", host, "/".join(parts[:-1]), parts[-1])
    parts = path.removesuffix(".git").split("/")
    if host and len(parts) >= 2:
        return Remote("unknown", host, "/".join(parts[:-1]), parts[-1])
    return Remote("unknown", host, "", "")


def detect() -> Remote:
    return parse_remote_url(origin_url())
