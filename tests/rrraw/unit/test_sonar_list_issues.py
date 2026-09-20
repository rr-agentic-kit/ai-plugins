"""Unit tests for rr-ci sonar-list-issues."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

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

import sonar_list_issues  # noqa: E402


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / ".git").mkdir()
    (tmp_path / "sonar-project.properties").write_text(
        "sonar.projectKey=demo_proj\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(sonar_list_issues, "repo_root", lambda: str(tmp_path))
    return tmp_path


def test_resolve_project_key_from_properties(repo: Path) -> None:
    assert sonar_list_issues._resolve_project_key(None) == "demo_proj"


def test_resolve_project_key_explicit_wins(repo: Path) -> None:
    assert sonar_list_issues._resolve_project_key("other.key") == "other.key"


def test_normalize_strips_project_prefix() -> None:
    issue = sonar_list_issues._normalize_issue(
        {
            "key": "k1",
            "rule": "python:S1",
            "severity": "MAJOR",
            "type": "BUG",
            "component": "demo_proj:src/a.py",
            "line": 3,
            "message": "x",
            "status": "OPEN",
        },
        "demo_proj",
    )
    assert issue["file"] == "src/a.py"
    assert issue["rule"] == "python:S1"


def test_main_succeeds_with_mocked_sonar(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = {
        "paging": {"total": 1},
        "issues": [
            {
                "key": "k1",
                "rule": "python:S1",
                "severity": "MAJOR",
                "type": "BUG",
                "component": "demo_proj:src/a.py",
                "line": 3,
                "message": "x",
                "status": "OPEN",
            }
        ],
    }

    def _fake_run(cmd: list[str], **_kwargs: Any) -> Any:
        assert cmd[:4] == ["sonar", "list", "issues", "-p"]
        assert "--pull-request" in cmd
        assert "14" in cmd

        class _Completed:
            returncode = 0
            stdout = json.dumps(payload)
            stderr = ""

        return _Completed()

    monkeypatch.setattr(sonar_list_issues.shutil, "which", lambda _: "/bin/sonar")
    monkeypatch.setattr(sonar_list_issues.subprocess, "run", _fake_run)
    code = sonar_list_issues.main(pull_request="14")
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is True
    assert out["result"]["total"] == 1
    assert out["result"]["issues"][0]["file"] == "src/a.py"
    assert out["result"]["pull_request"] == "14"


def test_main_fails_when_sonar_missing(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sonar_list_issues.shutil, "which", lambda _: None)
    code = sonar_list_issues.main(pull_request="1")
    assert code == 1
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is False
    assert out["error"]["code"] == "sonar_not_found"


def test_main_auto_resolves_open_pr(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = {
        "paging": {"total": 0},
        "issues": [],
    }

    def _fake_run(cmd: list[str], **_kwargs: Any) -> Any:
        assert "--pull-request" in cmd
        assert "42" in cmd

        class _Completed:
            returncode = 0
            stdout = json.dumps(payload)
            stderr = ""

        return _Completed()

    monkeypatch.setattr(sonar_list_issues.shutil, "which", lambda _: "/bin/sonar")
    monkeypatch.setattr(
        sonar_list_issues,
        "_open_pr_for_current_branch",
        lambda: "42",
    )
    monkeypatch.setattr(sonar_list_issues.subprocess, "run", _fake_run)
    code = sonar_list_issues.main()
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["result"]["pull_request"] == "42"
    assert out["result"]["total"] == 0
