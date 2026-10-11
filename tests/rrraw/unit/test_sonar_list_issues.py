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
    / "s-ci"
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
        # total stays 0, so `_run_sonar` falls back from `sonar list issues`
        # (--pull-request flag) to `sonar api get` (pullRequest= query param).
        if cmd[1:3] == ["list", "issues"]:
            assert "--pull-request" in cmd
            assert "42" in cmd
        else:
            assert cmd[1:3] == ["api", "get"]
            assert "pullRequest=42" in cmd[3]

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


def _issue(key: str, rule: str = "ts:S1") -> dict[str, Any]:
    return {
        "key": key,
        "rule": rule,
        "severity": "MINOR",
        "type": "CODE_SMELL",
        "component": "demo_proj:src/a.ts",
        "line": 1,
        "message": "m",
        "status": "OPEN",
    }


def _completed(payload: dict[str, Any]) -> Any:
    class _Completed:
        returncode = 0
        stdout = json.dumps(payload)
        stderr = ""

    return _Completed()


def test_resolve_organization_from_properties(repo: Path) -> None:
    (repo / "sonar-project.properties").write_text(
        "sonar.organization=acme\nsonar.projectKey=demo_proj\n", encoding="utf-8"
    )
    assert sonar_list_issues._resolve_organization(None, "demo_proj") == "acme"
    assert sonar_list_issues._resolve_organization("other", "demo_proj") == "other"


def test_scope_overall_queries_api_with_organization(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (repo / "sonar-project.properties").write_text(
        "sonar.organization=acme\nsonar.projectKey=demo_proj\n", encoding="utf-8"
    )
    calls: list[list[str]] = []

    def _fake_run(cmd: list[str], **_kwargs: Any) -> Any:
        calls.append(cmd)
        return _completed({"paging": {"total": 1}, "issues": [_issue("k1")]})

    monkeypatch.setattr(sonar_list_issues.shutil, "which", lambda _: "/bin/sonar")
    monkeypatch.setattr(sonar_list_issues.subprocess, "run", _fake_run)
    assert sonar_list_issues.main(scope="overall", lean=True) == 0
    out = json.loads(capsys.readouterr().out)["result"]
    assert [c[1:3] for c in calls] == [["api", "get"]]  # no CLI list call
    assert "organization=acme" in calls[0][3]
    assert "sinceLeakPeriod" not in calls[0][3]
    assert out["scope"] == "overall"
    assert out["source"] == "api"
    assert out["by_file"]["src/a.ts"][0]["type"] == "CODE_SMELL"


def test_scope_new_code_sets_leak_period(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []

    def _fake_run(cmd: list[str], **_kwargs: Any) -> Any:
        calls.append(cmd)
        return _completed({"paging": {"total": 0}, "issues": []})

    monkeypatch.setattr(sonar_list_issues.shutil, "which", lambda _: "/bin/sonar")
    monkeypatch.setattr(sonar_list_issues.subprocess, "run", _fake_run)
    assert sonar_list_issues.main(scope="new-code") == 0
    assert "sinceLeakPeriod=true" in calls[0][3]


def test_cli_zero_is_cross_checked_via_api_without_pr_scope(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """CLI auth-org mismatch: `sonar list issues` says 0, API says 1."""

    def _fake_run(cmd: list[str], **_kwargs: Any) -> Any:
        if cmd[1:3] == ["list", "issues"]:
            return _completed({"paging": {"total": 0}, "issues": []})
        return _completed({"paging": {"total": 1}, "issues": [_issue("k1")]})

    monkeypatch.setattr(sonar_list_issues.shutil, "which", lambda _: "/bin/sonar")
    monkeypatch.setattr(sonar_list_issues, "_open_pr_for_current_branch", lambda: "7")
    monkeypatch.setattr(sonar_list_issues.subprocess, "run", _fake_run)
    assert sonar_list_issues.main() == 0
    out = json.loads(capsys.readouterr().out)["result"]
    assert out["total"] == 1
    assert out["source"] == "api"


def test_api_search_pages_past_one_page(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sonar_list_issues, "_PAGE_SIZE", 2)
    pages = {
        "p=1": [_issue("a"), _issue("b")],
        "p=2": [_issue("c")],
    }

    def _fake_run(cmd: list[str], **_kwargs: Any) -> Any:
        page = "p=1" if "p=1" in cmd[3] else "p=2"
        return _completed({"paging": {"total": 3}, "issues": pages[page]})

    monkeypatch.setattr(sonar_list_issues.subprocess, "run", _fake_run)
    issues, total = sonar_list_issues._run_sonar_api_search(
        project="demo_proj",
        organization=None,
        pull_request=None,
        branch=None,
        new_code=False,
        statuses="OPEN",
    )
    assert total == 3
    assert [i["key"] for i in issues] == ["a", "b", "c"]


def test_scope_conflicts_with_pull_request(repo: Path) -> None:
    with pytest.raises(sonar_list_issues.SonarError) as exc:
        sonar_list_issues._resolve_scope("1", None, "overall")
    assert exc.value.code == "invalid_scope"
