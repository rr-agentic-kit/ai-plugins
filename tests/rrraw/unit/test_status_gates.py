"""Spec/status DoR gates, PRD status scope, deprecate/supersede (in-memory)."""

from __future__ import annotations

import validate_planning_script as vp
from helpers import error_codes, item


def test_status_on_non_prd_fails():
    issues = vp.check_required_fields(
        [item("ES-1", parent=None, moscow="Must", status="delivered")]
    )
    assert "STATUS_SCOPE" in error_codes(issues)


def test_status_on_prd_leaf_ok():
    issues = vp.check_required_fields(
        [item("PRD-1.1", parent="PRD-1", moscow="Must", status="delivered")]
    )
    assert error_codes(issues) == set()


def test_ready_cross_doc_parent_must_be_ready():
    issues = vp.check_status(
        [
            item("BRD-1", parent="MRD-1", spec="draft", moscow="Must"),
            item("PRD-1.1", parent="BRD-1", moscow="Must"),
        ]
    )
    assert "PARENT_READY" in error_codes(issues)


def test_same_doc_container_draft_child_ready_ok():
    issues = vp.check_status(
        [
            item("PRD-1", parent="BRD-1", kind="container", spec="draft"),
            item("PRD-1.1", parent="PRD-1", moscow="Must"),
        ]
    )
    assert "PARENT_READY" not in error_codes(issues)


def test_ready_placeholder_rank_is_dor():
    issues = vp.check_status([item("ES-1", parent=None, moscow=None)])
    assert "DOR" in error_codes(issues)


def test_idea_omitted_moscow_ok():
    issues = vp.check_status([item("ES-1", parent=None, spec="idea")])
    assert "DOR" not in error_codes(issues)
    assert (
        error_codes(vp.check_required_fields([item("ES-1", parent=None, spec="idea")]))
        == set()
    )


def test_idea_with_children_fails():
    issues = vp.check_kind_and_children(
        [
            item("ES-1", parent=None, kind="container", spec="idea"),
            item("ES-1.1", parent="ES-1", spec="idea"),
        ]
    )
    assert "IDEA_CHILDREN" in error_codes(issues)


def test_supersede_pair():
    issues = vp.check_parents(
        [
            item(
                "PRD-1.1",
                parent="PRD-1",
                spec="deprecated",
                moscow="Must",
                superseded_by="PRD-2",
            ),
            item(
                "PRD-2",
                parent="BRD-1",
                spec="draft",
                moscow="Must",
                supersedes="PRD-1.1",
            ),
        ]
    )
    assert "BROKEN_SUPERSEDE" not in error_codes(issues)
    assert "SUPERSEDE_PAIR" not in error_codes(issues)


def test_revive_deprecated_fails():
    issues = vp.check_revive(
        [item("ES-1", parent=None, moscow="Must")],
        {"ES-1": {"spec": "deprecated"}},
    )
    assert "REVIVE" in error_codes(issues)
