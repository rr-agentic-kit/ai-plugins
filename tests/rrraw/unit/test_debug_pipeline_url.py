"""Unit tests for debug-pipeline URL/id paths on GitHub and GitLab backends."""

from __future__ import annotations

import json
import sys
from argparse import Namespace
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

import debug_pipeline  # noqa: E402
import github_backend  # noqa: E402
import paths  # noqa: E402


class _FakeGlab:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[str] | str]] = []

    def api(self, path: str, **_kwargs: Any) -> Any:
        self.calls.append(("api", path))
        if path.endswith("/jobs/777"):
            return {
                "id": 777,
                "name": "test",
                "status": "failed",
                "pipeline": {
                    "id": 555,
                    "web_url": "https://gitlab.com/a/b/-/pipelines/555",
                },
            }
        if path.endswith("/pipelines/555"):
            return {
                "status": "failed",
                "web_url": "https://gitlab.com/a/b/-/pipelines/555",
            }
        if path.endswith("/pipelines/555/jobs"):
            return [{"id": 777, "name": "test", "status": "failed"}]
        if path.endswith("/pipelines/555/bridges"):
            return []
        return []

    def cli(self, args: list[str]) -> str:
        self.calls.append(("cli", args))
        if args[:2] == ["ci", "trace"]:
            return "ERROR: test failed\n"
        return ""


class _FakeGh:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def cli(self, args: list[str]) -> str:
        self.calls.append(args)
        if args[:2] == ["run", "list"]:
            return json.dumps(
                [
                    {
                        "databaseId": 111,
                        "status": "completed",
                        "conclusion": "failure",
                        "url": "https://github.com/acme/app/actions/runs/111",
                    }
                ]
            )
        if args[:3] == ["run", "view", "111"] and "--json" in args:
            fields_idx = args.index("--json") + 1
            fields = args[fields_idx]
            if fields == "jobs":
                return json.dumps(
                    {
                        "jobs": [
                            {
                                "databaseId": 222,
                                "name": "build",
                                "conclusion": "failure",
                                "steps": [
                                    {"name": "Checkout", "conclusion": "success"},
                                    {"name": "Test", "conclusion": "failure"},
                                ],
                            }
                        ]
                    }
                )
            return json.dumps(
                {
                    "databaseId": 111,
                    "status": "completed",
                    "conclusion": "failure",
                    "url": "https://github.com/acme/app/actions/runs/111",
                }
            )
        if args[:2] == ["run", "view"] and "--log-failed" in args:
            return "ERROR: npm test failed\n"
        if args[:2] == ["run", "download"]:
            return ""
        return ""


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / ".git").mkdir()
    monkeypatch.setattr(paths, "repo_root", lambda: str(tmp_path))
    return tmp_path


def test_gitlab_job_url_direct(repo: Path) -> None:
    glab = _FakeGlab()
    code = debug_pipeline.main(
        ref="https://gitlab.com/acme/app/-/jobs/777",
        save_log=True,
        glab=glab,
    )
    assert code == 1
    assert any(
        call[1][:2] == ["ci", "trace"] for call in glab.calls if call[0] == "cli"
    )
    assert (repo / ".ai" / "ci" / "job-777.log").is_file()


def test_gitlab_pipeline_url(repo: Path) -> None:
    glab = _FakeGlab()
    code = debug_pipeline.main(
        ref="https://gitlab.com/acme/app/-/pipelines/555",
        save_log=False,
        glab=glab,
    )
    assert code == 1
    assert any("pipelines/555/jobs" in str(call) for call in glab.calls)


def test_github_branch_fallback_status_normalization(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Branch fallback calls gitutil.current_branch() in cwd; CI checkouts are
    # often detached HEAD, so pin the branch instead of depending on the worktree.
    monkeypatch.setattr(github_backend, "current_branch", lambda: "feat/ci-fix")
    gh = _FakeGh()
    args = Namespace(
        ref=None,
        run_id=None,
        job_id=None,
        save_log=True,
        artifacts=False,
    )
    code = github_backend._debug_pipeline(gh, args)
    assert code == 1
    assert any(
        call[:2] == ["run", "list"] and "--branch" in call and "feat/ci-fix" in call
        for call in gh.calls
    )
    payload = _last_github_result(gh, monkeypatch)
    assert payload["status"] == "failed_job"
    assert payload["failed_job_id"] == "222"
    assert payload["failed_job_name"] == "build"
    assert payload["failed_step"] == "Test"
    assert payload["run_url"] == "https://github.com/acme/app/actions/runs/111"
    assert (repo / ".ai" / "ci" / "job-222.log").is_file()


def test_github_explicit_run_url_cross_repo(repo: Path) -> None:
    gh = _FakeGh()

    def cli(args: list[str]) -> str:
        if args[:2] == ["run", "view"] and "999" in args:
            if "--json" in args:
                fields = args[args.index("--json") + 1]
                if fields == "jobs":
                    return json.dumps(
                        {
                            "jobs": [
                                {
                                    "databaseId": 333,
                                    "name": "lint",
                                    "conclusion": "failure",
                                    "steps": [
                                        {"name": "Lint", "conclusion": "failure"}
                                    ],
                                }
                            ]
                        }
                    )
                return json.dumps(
                    {
                        "databaseId": 999,
                        "status": "completed",
                        "conclusion": "failure",
                        "url": "https://github.com/other/repo/actions/runs/999",
                    }
                )
            if "--log-failed" in args:
                return "ERROR: lint\n"
        return _FakeGh.cli(gh, args)

    gh.cli = cli  # type: ignore[method-assign]
    args = Namespace(
        ref="https://github.com/other/repo/actions/runs/999",
        run_id=None,
        job_id=None,
        save_log=False,
        artifacts=True,
    )
    code = github_backend._debug_pipeline(gh, args)
    assert code == 1
    assert any("--repo" in call and "other/repo" in call for call in gh.calls)
    artifacts_dir = repo / ".ai" / "ci" / "artifacts" / "333"
    assert artifacts_dir.is_dir()


def test_github_forge_mismatch() -> None:
    gh = _FakeGh()
    args = Namespace(
        ref="https://gitlab.com/acme/app/-/jobs/1",
        run_id=None,
        job_id=None,
        save_log=False,
        artifacts=False,
    )
    code = github_backend._debug_pipeline(gh, args)
    assert code == 1


def test_gitlab_forge_mismatch() -> None:
    glab = _FakeGlab()
    code = debug_pipeline.main(
        ref="https://github.com/acme/app/actions/runs/1",
        glab=glab,
    )
    assert code == 1


def _last_github_result(gh: _FakeGh, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    # Indirect: re-run minimal path and inspect via monkeypatched emit if needed.
    # Here we re-invoke logic by checking file + call args; for status use a fresh call.
    monkeypatch.setattr(github_backend, "current_branch", lambda: "feat/ci-fix")
    args = Namespace(
        ref=None, run_id=None, job_id=None, save_log=False, artifacts=False
    )
    captured: dict[str, Any] = {}

    def fake_succeed(
        command: str, result: dict[str, Any] | None = None, *, exit_code: int = 0
    ) -> int:
        captured.update(result or {})
        return exit_code

    import emit

    monkeypatch.setattr(emit, "succeed", fake_succeed)
    github_backend._debug_pipeline(gh, args)
    return captured
