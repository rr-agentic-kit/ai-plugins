"""Parse GitHub/GitLab CI run/job/pipeline URLs."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from errors import CiUrlError

_GH_RUN = re.compile(
    r"^https?://(?P<host>[^/]+)/(?P<owner>[^/]+)/(?P<repo>[^/]+)/actions/runs/(?P<run_id>\d+)(?:/job/(?P<job_id>\d+))?/?$",
    re.IGNORECASE,
)
_GITLAB_PIPELINE = re.compile(
    r"^https?://(?P<host>[^/]+)/(?P<path>.+?)/-/pipelines/(?P<run_id>\d+)/?$",
    re.IGNORECASE,
)
_GITLAB_JOB = re.compile(
    r"^https?://(?P<host>[^/]+)/(?P<path>.+?)/-/jobs/(?P<job_id>\d+)/?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CiUrl:
    forge: str
    host: str
    owner: str
    repo: str
    run_id: str | None
    job_id: str | None


def is_ci_url(ref: str | None) -> bool:
    if not ref:
        return False
    stripped = ref.strip()
    return stripped.startswith("http://") or stripped.startswith("https://")


def _split_gitlab_path(path: str) -> tuple[str, str]:
    parts = path.rstrip("/").split("/")
    if len(parts) < 2:
        return "", parts[0] if parts else ""
    return "/".join(parts[:-1]), parts[-1]


def parse_ci_url(url: str) -> CiUrl | None:
    """Return parsed CI URL fields, or None when the URL is not a supported CI link."""
    normalized = url.strip()
    if not normalized:
        return None

    gh = _GH_RUN.match(normalized)
    if gh:
        return CiUrl(
            forge="github",
            host=gh.group("host").lower(),
            owner=gh.group("owner"),
            repo=gh.group("repo"),
            run_id=gh.group("run_id"),
            job_id=gh.group("job_id"),
        )

    gl_job = _GITLAB_JOB.match(normalized)
    if gl_job:
        owner, repo = _split_gitlab_path(gl_job.group("path"))
        return CiUrl(
            forge="gitlab",
            host=gl_job.group("host").lower(),
            owner=owner,
            repo=repo,
            run_id=None,
            job_id=gl_job.group("job_id"),
        )

    gl_pipe = _GITLAB_PIPELINE.match(normalized)
    if gl_pipe:
        owner, repo = _split_gitlab_path(gl_pipe.group("path"))
        return CiUrl(
            forge="gitlab",
            host=gl_pipe.group("host").lower(),
            owner=owner,
            repo=repo,
            run_id=gl_pipe.group("run_id"),
            job_id=None,
        )

    parsed = urlparse(normalized)
    host = (parsed.hostname or "").lower()
    if host and ("github" in host or "gitlab" in host):
        return None
    return None


def parse_ci_url_or_raise(url: str) -> CiUrl:
    parsed = parse_ci_url(url)
    if parsed is None:
        raise CiUrlError("invalid_url", f"unsupported CI URL: {url}")
    return parsed
