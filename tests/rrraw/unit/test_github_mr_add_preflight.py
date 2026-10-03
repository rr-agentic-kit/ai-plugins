"""Unit tests for GitHub mr-add-preflight open-PR detection."""

from __future__ import annotations

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

import emit  # noqa: E402
import github_backend  # noqa: E402
from errors import GhError  # noqa: E402


class _FakeGh:
    def __init__(self, *, handler: Any) -> None:
        self.calls: list[list[str]] = []
        self._handler = handler

    def cli(self, args: list[str]) -> str:
        self.calls.append(args)
        return self._handler(args)


def _capture_emit(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []

    def _write(
        command: str,
        *,
        ok: bool,
        result: dict[str, Any] | None = None,
        error: Any = None,
    ) -> None:
        payloads.append(
            {
                "command": command,
                "ok": ok,
                "result": result,
                "error": (
                    None
                    if error is None
                    else {"code": error.code, "message": error.message}
                ),
            }
        )

    monkeypatch.setattr(emit, "write", _write)
    return payloads


def test_add_preflight_exists_uses_positional_branch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payloads = _capture_emit(monkeypatch)
    monkeypatch.setattr(github_backend, "repo_root", lambda: "/tmp/repo")
    monkeypatch.setattr(github_backend, "current_branch", lambda: "feat/x")
    monkeypatch.setattr(github_backend, "resolve_pr_base", lambda _base: "main")

    def handler(args: list[str]) -> str:
        assert args[:3] == ["pr", "view", "feat/x"]
        assert "--head" not in args
        return "https://github.com/acme/app/pull/9\n"

    gh = _FakeGh(handler=handler)
    code = github_backend._add_preflight(gh, Namespace(branch_name=None, base=None))
    assert code == 0
    assert payloads[-1]["ok"] is True
    assert payloads[-1]["result"]["status"] == "exists"
    assert payloads[-1]["result"]["mr_url"] == "https://github.com/acme/app/pull/9"


def test_add_preflight_ready_create_on_no_pr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payloads = _capture_emit(monkeypatch)
    monkeypatch.setattr(github_backend, "repo_root", lambda: "/tmp/repo")
    monkeypatch.setattr(github_backend, "current_branch", lambda: "feat/x")
    monkeypatch.setattr(github_backend, "resolve_pr_base", lambda _base: "main")

    def handler(args: list[str]) -> str:
        raise GhError(
            "gh pr view feat/x --json url --jq .url failed",
            stderr='no pull requests found for branch "feat/x"',
        )

    gh = _FakeGh(handler=handler)
    code = github_backend._add_preflight(gh, Namespace(branch_name=None, base=None))
    assert code == 0
    assert payloads[-1]["result"]["status"] == "ready_create"


def test_add_preflight_probe_failure_does_not_ready_create(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(github_backend, "repo_root", lambda: "/tmp/repo")
    monkeypatch.setattr(github_backend, "current_branch", lambda: "feat/x")
    monkeypatch.setattr(github_backend, "resolve_pr_base", lambda _base: "main")

    def handler(args: list[str]) -> str:
        raise GhError(
            "gh pr view feat/x --json url --jq .url --head feat/x failed",
            stderr="unknown flag: --head",
        )

    gh = _FakeGh(handler=handler)
    args = Namespace(branch_name=None, base=None)
    with pytest.raises(GhError, match="failed"):
        github_backend._add_preflight(gh, args)


def test_pr_number_uses_positional_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(github_backend, "current_branch", lambda: "feat/x")
    calls: list[list[str]] = []

    class _Gh:
        def cli(self, args: list[str]) -> str:
            calls.append(args)
            return "25\n"

    number = github_backend._pr_number(_Gh(), None)
    assert number == "25"
    assert calls[0][:3] == ["pr", "view", "feat/x"]
    assert "--head" not in calls[0]


def test_gh_no_open_pr_helper() -> None:
    assert github_backend._gh_no_open_pr(
        GhError("failed", stderr='no pull requests found for branch "x"')
    )
    assert not github_backend._gh_no_open_pr(
        GhError("failed", stderr="unknown flag: --head")
    )
