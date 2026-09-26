"""Unit tests for create_pr.py."""

from __future__ import annotations

import pytest

import create_pr as cpr


def test_reserved_head_rejected(fake_gh, fake_git, monkeypatch):
    fake_git.current_branch = "master"
    monkeypatch.setattr(cpr, "require_gh", lambda *_a, **_k: None)
    monkeypatch.setattr(cpr, "GhRunner", lambda repo=None: fake_gh)
    monkeypatch.setattr(cpr, "GitRunner", lambda: fake_git)

    with pytest.raises(SystemExit):
        cpr.main(["--title", "t", "--description", "d"])


def test_creates_pr(fake_gh, fake_git, monkeypatch, capsys):
    fake_gh.branches = ["release/0.1.0"]
    fake_git.current_branch = "feat/x"
    fake_git.remote_branches.add("feat/x")
    monkeypatch.setattr(cpr, "require_gh", lambda *_a, **_k: None)
    monkeypatch.setattr(cpr, "GhRunner", lambda repo=None: fake_gh)
    monkeypatch.setattr(cpr, "GitRunner", lambda: fake_git)
    monkeypatch.setattr(
        cpr,
        "list_release_branches",
        lambda *_a, **_k: ["release/0.1.0"],
    )

    assert cpr.main(["--title", "Add thing", "--description", "Body"]) == 0
    out = capsys.readouterr().out
    assert "status=created" in out
    assert fake_gh.calls[-1][0][:2] == ("pr", "create")


def test_updates_existing_pr(fake_gh, fake_git, monkeypatch, capsys):
    fake_gh.branches = ["release/0.1.0"]
    fake_gh.prs["42"] = {
        "url": "https://github.com/example/pr/42",
        "number": "42",
        "head": "feat/x",
    }
    fake_git.current_branch = "feat/x"
    fake_git.remote_branches.add("feat/x")
    monkeypatch.setattr(cpr, "require_gh", lambda *_a, **_k: None)
    monkeypatch.setattr(cpr, "GhRunner", lambda repo=None: fake_gh)
    monkeypatch.setattr(cpr, "GitRunner", lambda: fake_git)
    monkeypatch.setattr(
        cpr,
        "list_release_branches",
        lambda *_a, **_k: ["release/0.1.0"],
    )

    assert cpr.main(["--title", "Updated", "--description", "New body"]) == 0
    out = capsys.readouterr().out
    assert "status=updated" in out
    assert fake_gh.calls[-1][0][:3] == ("pr", "edit", "42")
