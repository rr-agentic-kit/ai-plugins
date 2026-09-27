"""Unit tests for CI run/job URL parsing."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = (
    Path(__file__).resolve().parents[3]
    / "plugins"
    / "rrraw"
    / "skills"
    / "s-ci"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS))

import ci_url  # noqa: E402
from errors import CiUrlError  # noqa: E402


def test_github_run_url() -> None:
    parsed = ci_url.parse_ci_url("https://github.com/acme/app/actions/runs/123456789")
    assert parsed is not None
    assert parsed.forge == "github"
    assert parsed.host == "github.com"
    assert parsed.owner == "acme"
    assert parsed.repo == "app"
    assert parsed.run_id == "123456789"
    assert parsed.job_id is None


def test_github_job_url() -> None:
    parsed = ci_url.parse_ci_url(
        "https://github.com/acme/app/actions/runs/123456789/job/987654321"
    )
    assert parsed is not None
    assert parsed.run_id == "123456789"
    assert parsed.job_id == "987654321"


def test_gitlab_pipeline_url() -> None:
    parsed = ci_url.parse_ci_url("https://gitlab.com/acme/app/-/pipelines/555")
    assert parsed is not None
    assert parsed.forge == "gitlab"
    assert parsed.host == "gitlab.com"
    assert parsed.owner == "acme"
    assert parsed.repo == "app"
    assert parsed.run_id == "555"
    assert parsed.job_id is None


def test_gitlab_job_url() -> None:
    parsed = ci_url.parse_ci_url("https://gitlab.com/group/sub/app/-/jobs/777")
    assert parsed is not None
    assert parsed.owner == "group/sub"
    assert parsed.repo == "app"
    assert parsed.job_id == "777"
    assert parsed.run_id is None


def test_self_hosted_gitlab_host() -> None:
    parsed = ci_url.parse_ci_url(
        "https://gitlab.company.internal/team/service/-/jobs/42"
    )
    assert parsed is not None
    assert parsed.forge == "gitlab"
    assert parsed.host == "gitlab.company.internal"
    assert parsed.owner == "team"
    assert parsed.repo == "service"
    assert parsed.job_id == "42"


def test_invalid_foreign_url() -> None:
    assert ci_url.parse_ci_url("https://example.com/not/ci") is None
    assert ci_url.parse_ci_url("https://github.com/acme/app/pull/1") is None


def test_parse_or_raise_invalid() -> None:
    with pytest.raises(CiUrlError) as exc:
        ci_url.parse_ci_url_or_raise("https://example.com/nope")
    assert exc.value.code == "invalid_url"


def test_is_ci_url() -> None:
    assert ci_url.is_ci_url("https://github.com/a/b/actions/runs/1")
    assert not ci_url.is_ci_url("42")
    assert not ci_url.is_ci_url(None)
