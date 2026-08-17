"""Spec/build DoR gates, class derivation, deprecate/supersede (in-memory)."""

from __future__ import annotations

import validate_planning_script as vp
from helpers import codes, error_codes, item, triad


def test_derived_class_partition():
    assert vp.derived_class("high", "high", "critical") == "must-correct"
    assert vp.derived_class("low", "high", "low") == "must-present"
    assert vp.derived_class("low", "low", "high") == "protect"
    assert vp.derived_class("high", "low", "low") == "leverage"
    assert vp.derived_class("low", "low", "low") == "optional"
    assert vp.derived_class("high", "moderate", "low") == "optional"


def test_class_mismatch():
    leaf = item(
        "FRD-1.1",
        parent="FRD-1",
        build="none",
        triad=triad(class_name="optional"),
    )
    issues = vp.check_status([leaf])
    assert "CLASS_MISMATCH" in error_codes(issues)


def test_build_on_draft_fails():
    leaf = item(
        "FRD-1.1",
        parent="FRD-1",
        spec="draft",
        build="in_progress",
        triad=triad(wrong="low", class_name="must-present"),
    )
    issues = vp.check_status([leaf])
    assert "BUILD_GATE" in error_codes(issues)


def test_build_on_prd_fails():
    issues = vp.check_required_fields(
        [item("PRD-1", parent="BRD-1", moscow="Must", build="done")]
    )
    assert "BUILD_SCOPE" in error_codes(issues)


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


def test_deprecated_in_progress_warns():
    leaf = item(
        "FRD-1.1",
        parent="FRD-1",
        spec="deprecated",
        build="in_progress",
        triad=triad(),
    )
    issues = vp.check_status([leaf])
    assert "DEPRECATED_BUILD" in codes(issues)
    assert "DEPRECATED_BUILD" not in error_codes(issues)
    assert "BUILD_GATE" in error_codes(issues)


def test_supersede_pair():
    issues = vp.check_parents(
        [
            item(
                "FRD-1.1",
                parent="FRD-1",
                spec="deprecated",
                build="none",
                triad=triad(),
                superseded_by="FRD-2",
            ),
            item(
                "FRD-2",
                parent="PRD-1.1",
                spec="draft",
                build="none",
                triad=triad(),
                supersedes="FRD-1.1",
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
