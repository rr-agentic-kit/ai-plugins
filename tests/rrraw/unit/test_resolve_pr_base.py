"""Unit tests for resolve_pr_base and mr-add-preflight base_branch envelope."""

from __future__ import annotations

import json
import subprocess
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

import gitutil  # noqa: E402
import mr_add_preflight_support as support  # noqa: E402


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _configure_identity(cwd: Path) -> None:
    _git(cwd, "config", "user.email", "test@example.com")
    _git(cwd, "config", "user.name", "test")


def _clone_worktree(tmp_path: Path) -> Path:
    remote = tmp_path / "remote.git"
    work = tmp_path / "work"
    _git(tmp_path, "init", "--bare", str(remote))
    _git(tmp_path, "clone", str(remote), str(work))
    _configure_identity(work)
    _git(work, "checkout", "-b", "main")
    (work / "README").write_text("root\n", encoding="utf-8")
    _git(work, "add", "README")
    _git(work, "commit", "-m", "init")
    _git(work, "push", "-u", "origin", "main")
    return work


def _commit_file(cwd: Path, name: str, body: str, message: str) -> None:
    (cwd / name).write_text(body, encoding="utf-8")
    _git(cwd, "add", name)
    _git(cwd, "commit", "-m", message)


def test_resolve_pr_base_explicit_wins(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    work = _clone_worktree(tmp_path)
    monkeypatch.chdir(work)
    assert gitutil.resolve_pr_base("develop") == "develop"
    assert gitutil.resolve_pr_base("origin/feature/x") == "feature/x"
    assert gitutil.resolve_pr_base("  origin/main  ") == "main"


def test_resolve_pr_base_trunk_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    work = _clone_worktree(tmp_path)
    _git(work, "checkout", "-b", "feature/leaf")
    _commit_file(work, "leaf.txt", "leaf\n", "leaf")
    monkeypatch.chdir(work)
    assert gitutil.resolve_pr_base() == "main"


def test_resolve_pr_base_follow_up_prefers_non_trunk_ancestor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    work = _clone_worktree(tmp_path)
    _git(work, "checkout", "-b", "feature/a")
    _commit_file(work, "a1.txt", "a1\n", "a1")
    _commit_file(work, "a2.txt", "a2\n", "a2")
    _git(work, "push", "-u", "origin", "feature/a")
    _git(work, "checkout", "-b", "feature/b")
    _commit_file(work, "b.txt", "b\n", "b")
    monkeypatch.chdir(work)
    assert gitutil.resolve_pr_base() == "feature/a"


def test_short_remote_branch_and_origin_ref() -> None:
    assert gitutil.short_remote_branch("origin/main") == "main"
    assert gitutil.short_remote_branch("main") == "main"
    assert gitutil.origin_ref_for_base("feature/a") == "origin/feature/a"
    assert gitutil.origin_ref_for_base("origin/main") == "origin/main"


def _parse_out(capsys: pytest.CaptureFixture[str]) -> dict[str, Any]:
    return json.loads(capsys.readouterr().out)


def test_mr_lookup_ready_create_emits_base_branch(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(support, "_lookup_open_mr_url", lambda _client, _branch: "")
    rc = support._mr_lookup_result(
        "feature/b", object(), base_branch="feature/a"  # type: ignore[arg-type]
    )
    assert rc == 0
    payload = _parse_out(capsys)
    assert payload["ok"] is True
    assert payload["result"]["status"] == "ready_create"
    assert payload["result"]["base_branch"] == "feature/a"


def test_mr_lookup_exists_emits_base_branch(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        support, "_lookup_open_mr_url", lambda _client, _branch: "https://example/mr/1"
    )
    rc = support._mr_lookup_result(
        "feature/b", object(), base_branch="feature/a"  # type: ignore[arg-type]
    )
    assert rc == 0
    payload = _parse_out(capsys)
    assert payload["result"]["status"] == "exists"
    assert payload["result"]["base_branch"] == "feature/a"
    assert payload["result"]["mr_url"] == "https://example/mr/1"


def test_run_after_snapshot_uses_explicit_base(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    seen: dict[str, str | None] = {}

    def fake_resolve(explicit: str | None = None) -> str:
        seen["explicit"] = explicit
        return "stacked-base"

    monkeypatch.setattr(support, "resolve_pr_base", fake_resolve)
    monkeypatch.setattr(support, "_run_preflight_gates", lambda *_a, **_k: None)
    monkeypatch.setattr(
        support,
        "_push_and_lookup_mr",
        lambda branch, base, client, *, base_branch, same_name_push: support.emit.succeed(
            support.COMMAND,
            support.emit_result(
                "ready_create",
                extra={
                    "base_branch": base_branch,
                    "message": f"base-ref={base}",
                },
            ),
        ),
    )

    rc = support._run_after_snapshot(
        "feature/b",
        object(),  # type: ignore[arg-type]
        continue_anyway=False,
        same_name_push=False,
        base="origin/stacked-base",
    )
    assert rc == 0
    assert seen["explicit"] == "origin/stacked-base"
    payload = _parse_out(capsys)
    assert payload["result"]["base_branch"] == "stacked-base"
    assert "origin/stacked-base" in payload["result"]["message"]


def test_escalate_merged_emits_base_branch(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(support, "already_merged", lambda _base: (True, "ancestor"))
    rc = support._merged_escalation(
        "origin/main", base_branch="main", continue_anyway=False
    )
    assert rc == 0
    payload = _parse_out(capsys)
    assert payload["result"]["status"] == "escalate_merged"
    assert payload["result"]["base_branch"] == "main"
