"""Unit tests for release.py maintainer CLI."""

from __future__ import annotations

import pytest

import release as rel
from release_branches import WORKFLOW


def test_resolve_branch_arg_defaults_to_lowest():
    branch = rel.resolve_branch_arg("release", None, ["release/0.2.0", "release/0.1.0"])
    assert branch == "release/0.1.0"


def test_resolve_branch_arg_hotfix_required():
    with pytest.raises(SystemExit):
        rel.resolve_branch_arg("hotfix", None, ["release/0.1.0"])


def test_workflow_ref_for_uses_default_branch_when_workflow_present(fake_git):
    fake_git.workflows.add("origin/master:.github/workflows/release-control.yml")
    from release_branches import workflow_ref_for

    ref = workflow_ref_for(
        fake_git,
        ["release/0.1.0"],
        repo_root=fake_git.repo_root,
        ref_override=None,
        target="release/0.1.0",
        default_branch_name="master",
    )
    assert ref == "master"


def test_dispatch_assembles_workflow_args(fake_gh, fake_git):
    fake_git.workflows.add("origin/master:.github/workflows/release-control.yml")
    rel.dispatch(
        fake_gh,
        fake_git,
        repo_root=fake_git.repo_root,
        branches=["release/0.1.0"],
        action="open",
        branch="release/0.1.0",
        ref_override=None,
        default_branch_name="master",
    )
    assert fake_gh.calls[0][0][:2] == ("workflow", "run")
    assert WORKFLOW in fake_gh.calls[0][0]


def test_cmd_seed_refuses_existing_branch(fake_gh, fake_git, monkeypatch):
    fake_gh.branches = ["release/0.1.0"]
    monkeypatch.setattr(
        rel,
        "list_release_branches",
        lambda *_a, **_k: ["release/0.1.0"],
    )
    monkeypatch.setattr(rel, "default_branch", lambda _gh: "master")

    with pytest.raises(SystemExit):
        rel.cmd_seed(
            fake_gh,
            fake_git,
            repo_root=fake_git.repo_root,
            branches=["release/0.1.0"],
            version="0.1.0",
            ref_override=None,
            default_branch_name="master",
            yes=True,
            input_fn=lambda _p: "y",
        )


def test_cmd_active_emits_lowest(fake_gh, fake_git, capsys, monkeypatch):
    monkeypatch.setattr(rel, "require_gh", lambda *_a, **_k: None)
    monkeypatch.setattr(
        rel,
        "list_release_branches",
        lambda *_a, **_k: ["release/0.2.0", "release/0.1.0"],
    )
    monkeypatch.setattr(rel, "default_branch", lambda _gh: "master")

    assert rel.main(["active"]) == 0
    assert "branch=release/0.1.0" in capsys.readouterr().out
