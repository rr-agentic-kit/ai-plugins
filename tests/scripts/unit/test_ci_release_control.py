"""Unit tests for ci_release_control branch parsing and outputs."""

from __future__ import annotations

import pytest

import ci_release_control as crc


def test_parse_release_branch_accepts_minor_zero():
    assert crc.parse_release_branch("release/0.1.0") == "0.1.0"


def test_parse_release_branch_rejects_patch_train():
    with pytest.raises(ValueError, match=r"must end in \.0"):
        crc.parse_release_branch("release/0.1.1")


def test_parse_hotfix_branch_accepts_patch():
    assert crc.parse_hotfix_branch("hotfix/0.1.1") == "0.1.1"


def test_parse_hotfix_branch_rejects_zero_patch():
    with pytest.raises(ValueError, match="patch must be > 0"):
        crc.parse_hotfix_branch("hotfix/0.1.0")


def test_next_minor_version():
    assert crc.next_minor_version("0.1.0") == "0.2.0"
    assert crc.next_minor_version("1.4.2") == "1.5.0"


def test_open_sets_rc1(mini_repo, monkeypatch, capsys):
    root = mini_repo(pyproject_version="0.0.6-rc-9", plugins={"foo": "0.0.6-rc-9"})
    monkeypatch.setattr(crc, "REPO_ROOT", root)
    monkeypatch.setattr(crc.bump, "REPO_ROOT", root)
    calls: list[list[str]] = []
    monkeypatch.setattr(
        crc.bump, "run_uv", lambda args, *, cwd: calls.append(list(args))
    )

    assert crc.main(["open", "--branch", "release/0.1.0", "--repo", str(root)]) == 0

    out = capsys.readouterr().out
    assert "version=0.1.0-rc-1" in out
    assert calls == [["lock"]]


def test_rc_ticks_prerelease(mini_repo, monkeypatch, capsys):
    root = mini_repo(pyproject_version="0.1.0-rc-1", plugins={"foo": "0.1.0-rc-1"})
    monkeypatch.setattr(crc, "REPO_ROOT", root)
    monkeypatch.setattr(crc.bump, "REPO_ROOT", root)
    monkeypatch.setattr(crc.bump, "run_uv", lambda *a, **k: None)

    assert crc.main(["rc", "--repo", str(root)]) == 0

    assert "version=0.1.0-rc-2" in capsys.readouterr().out


def test_promote_emits_next_branch(mini_repo, monkeypatch, capsys):
    root = mini_repo(pyproject_version="0.1.0-rc-3", plugins={"foo": "0.1.0-rc-3"})
    monkeypatch.setattr(crc, "REPO_ROOT", root)
    monkeypatch.setattr(crc.bump, "REPO_ROOT", root)
    monkeypatch.setattr(
        crc.bump,
        "run_bump",
        lambda kind, repo: "0.1.0" if kind == "stable" else pytest.fail("unexpected"),
    )

    assert crc.main(["promote", "--branch", "release/0.1.0", "--repo", str(root)]) == 0

    out = capsys.readouterr().out
    assert "version=0.1.0" in out
    assert "next_version=0.2.0" in out
    assert "next_branch=release/0.2.0" in out


def test_promote_rejects_branch_version_mismatch(mini_repo, monkeypatch):
    root = mini_repo(pyproject_version="0.1.0-rc-1", plugins={"foo": "0.1.0-rc-1"})
    monkeypatch.setattr(crc.bump, "run_bump", lambda *_a, **_k: "0.9.0")

    assert crc.main(["promote", "--branch", "release/0.1.0", "--repo", str(root)]) == 1


def test_hotfix_sets_patch_version(mini_repo, monkeypatch, capsys):
    root = mini_repo(pyproject_version="0.1.0", plugins={"foo": "0.1.0"})
    monkeypatch.setattr(crc.bump, "REPO_ROOT", root)
    calls: list[list[str]] = []
    monkeypatch.setattr(
        crc.bump, "run_uv", lambda args, *, cwd: calls.append(list(args))
    )

    assert crc.main(["hotfix", "--branch", "hotfix/0.1.1", "--repo", str(root)]) == 0

    out = capsys.readouterr().out
    assert "version=0.1.1" in out
    assert calls == [["lock"]]


def test_next_minor_reads_pyproject(mini_repo, monkeypatch, capsys):
    root = mini_repo(pyproject_version="0.3.0", plugins={"foo": "0.3.0"})
    assert crc.main(["next-minor", "--repo", str(root)]) == 0
    out = capsys.readouterr().out
    assert "next_version=0.4.0" in out
    assert "next_branch=release/0.4.0" in out
