"""Unit tests for rr-git finish_commit_preflight."""

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

import finish_commit_preflight  # noqa: E402


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


def test_hooks_likely_detects_husky(tmp_path: Path) -> None:
    _git_init(tmp_path)
    husky = tmp_path / ".husky"
    husky.mkdir()
    (husky / "pre-commit").write_text("#!/bin/sh\n", encoding="utf-8")
    assert finish_commit_preflight._hooks_likely(tmp_path) is True


def test_main_warn_when_many_staged_with_hooks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _git_init(tmp_path)
    (tmp_path / ".husky").mkdir()
    (tmp_path / ".husky" / "pre-commit").write_text("#!/bin/sh\n", encoding="utf-8")
    for i in range(3):
        f = tmp_path / f"f{i}.txt"
        f.write_text("x\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", f.name], cwd=tmp_path, check=True, capture_output=True
        )
    rc = finish_commit_preflight.main(
        ["--repo", str(tmp_path), "--warn-threshold", "2"]
    )
    out = capsys.readouterr().out
    assert rc == 0
    assert "status=ok" in out
    assert "staged_count=3" in out
    assert "hooks_likely=yes" in out
    assert "warn=yes" in out
