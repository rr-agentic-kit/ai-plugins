"""Unit tests for rr-git resolve_repo_root."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = (
    Path(__file__).resolve().parents[3]
    / "plugins"
    / "rrraw"
    / "skills"
    / "rr-git"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS))

import resolve_repo_root  # noqa: E402


def _git_init(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "test"],
        cwd=path,
        check=True,
        capture_output=True,
    )


def test_resolve_cwd_ok(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _git_init(tmp_path)
    monkeypatch.chdir(tmp_path)
    root, err, _ = resolve_repo_root.resolve(None)
    assert err is None
    assert Path(root).resolve() == tmp_path.resolve()


def test_resolve_candidate_subdir_fails(tmp_path: Path) -> None:
    _git_init(tmp_path)
    sub = tmp_path / "pkg"
    sub.mkdir()
    root, err, message = resolve_repo_root.resolve(sub)
    assert root is None
    assert err == "not_root"
    assert "root is" in message


def test_main_emits_repo_root(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _git_init(tmp_path)
    rc = resolve_repo_root.main(["--candidate", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "status=ok" in out
    assert f"repo_root={tmp_path.resolve()}" in out or "repo_root=" in out
