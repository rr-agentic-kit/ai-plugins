"""rr-ci disk sidecars land under `.ai/ci/`."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = (
    Path(__file__).resolve().parents[3]
    / "plugins"
    / "rrraw"
    / "skills"
    / "rr-ci"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS))

import debug_pipeline  # noqa: E402
import paths  # noqa: E402


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / ".git").mkdir()
    monkeypatch.setattr(paths, "repo_root", lambda: str(tmp_path))
    return tmp_path


def test_ci_file_under_ai_ci(repo: Path) -> None:
    target = paths.ci_file("job-42.log")
    assert target == repo / ".ai" / "ci" / "job-42.log"
    assert (repo / ".ai" / "ci").is_dir()
    assert paths.ci_rel(target) == ".ai/ci/job-42.log"


def test_ci_file_strips_path_traversal(repo: Path) -> None:
    target = paths.ci_file("../escape.log")
    assert target.parent == repo / ".ai" / "ci"
    assert target.name == "escape.log"


def test_save_log_writes_under_ai_ci(repo: Path) -> None:
    result = debug_pipeline._failed_job_result(
        {"failed_job_id": "99"},
        ["boom"],
        "full trace\n",
        save_log=True,
    )
    assert result["log_path"] == ".ai/ci/job-99.log"
    assert (repo / ".ai" / "ci" / "job-99.log").read_text(encoding="utf-8") == (
        "full trace\n"
    )


def test_no_save_log_skips_disk(repo: Path) -> None:
    result = debug_pipeline._failed_job_result(
        {"failed_job_id": "1"},
        [],
        "x",
        save_log=False,
    )
    assert "log_path" not in result
    assert not (repo / ".ai").exists()
