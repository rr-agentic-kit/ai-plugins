"""Unit tests for branch_new.py."""

from __future__ import annotations

import pytest

import branch_new as bn


def test_reserved_branch_name_rejected():
    with pytest.raises(SystemExit):
        bn.main(["release/0.1.0"])


def test_creates_branch_from_lowest_release(fake_gh, fake_git, monkeypatch):
    fake_gh.branches = ["release/0.1.0"]
    monkeypatch.setattr(bn, "require_gh", lambda *_a, **_k: None)
    monkeypatch.setattr(bn, "GhRunner", lambda repo=None: fake_gh)
    monkeypatch.setattr(bn, "GitRunner", lambda: fake_git)
    monkeypatch.setattr(
        bn,
        "list_release_branches",
        lambda *_a, **_k: ["release/0.1.0"],
    )

    assert bn.main(["feat/foo"]) == 0

    checkout = next(call for call in fake_git.calls if call[0][0] == "checkout")
    assert checkout[0][-1] == "origin/release/0.1.0"
    push = next(call for call in fake_git.calls if call[0][0] == "push")
    assert push[0][-1] == "feat/foo"


def test_no_push_skips_remote(fake_gh, fake_git, monkeypatch):
    fake_gh.branches = ["release/0.1.0"]
    monkeypatch.setattr(bn, "require_gh", lambda *_a, **_k: None)
    monkeypatch.setattr(bn, "GhRunner", lambda repo=None: fake_gh)
    monkeypatch.setattr(bn, "GitRunner", lambda: fake_git)
    monkeypatch.setattr(
        bn,
        "list_release_branches",
        lambda *_a, **_k: ["release/0.1.0"],
    )

    assert bn.main(["feat/bar", "--no-push"]) == 0
    assert not any(call[0][0] == "push" for call in fake_git.calls)
