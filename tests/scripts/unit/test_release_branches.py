"""Unit tests for release branch helpers."""

from __future__ import annotations

import pytest

import release_branches as rb


def test_sorted_release_branches_orders_by_semver():
    branches = ["release/0.2.0", "release/0.10.0", "release/0.1.0", "hotfix/0.1.1"]
    assert rb.sorted_release_branches(branches) == [
        "release/0.1.0",
        "release/0.2.0",
        "release/0.10.0",
    ]


def test_lowest_open_release():
    assert rb.lowest_open_release(["release/0.2.0", "release/0.1.0"]) == "release/0.1.0"


def test_lowest_open_release_empty_raises():
    with pytest.raises(SystemExit):
        rb.lowest_open_release([])


def test_pick_release_branch_explicit():
    picked = rb.pick_release_branch(
        ["release/0.1.0", "release/0.2.0"],
        "release/0.2.0",
        is_tty=False,
    )
    assert picked == "release/0.2.0"


def test_pick_release_branch_sole():
    assert (
        rb.pick_release_branch(["release/0.3.0"], None, is_tty=False) == "release/0.3.0"
    )


def test_pick_release_branch_multi_non_tty_fails():
    with pytest.raises(SystemExit):
        rb.pick_release_branch(
            ["release/0.1.0", "release/0.2.0"],
            None,
            is_tty=False,
        )


def test_pick_release_branch_interactive_choice():
    picked = rb.pick_release_branch(
        ["release/0.1.0", "release/0.2.0"],
        None,
        input_fn=lambda _prompt: "2",
        is_tty=True,
    )
    assert picked == "release/0.2.0"


def test_validate_release_branch_name_rejects_hotfix():
    with pytest.raises(SystemExit):
        rb.validate_release_branch_name("hotfix/0.1.1")


def test_is_reserved_branch_name():
    assert rb.is_reserved_branch_name("release/0.1.0")
    assert rb.is_reserved_branch_name("master")
    assert not rb.is_reserved_branch_name("feat/foo")


def test_workflow_ref_for_prefers_ref_override(fake_git):
    ref = rb.workflow_ref_for(
        fake_git,
        ["release/0.1.0"],
        repo_root=fake_git.repo_root,
        ref_override="custom",
        target="release/0.1.0",
        default_branch_name="master",
    )
    assert ref == "custom"
