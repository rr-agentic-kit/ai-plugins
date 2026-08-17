"""Graph, numbering, and parent-walk tests (in-memory)."""

from __future__ import annotations

import validate_planning_script as vp
from helpers import error_codes, item, triad


def test_broken_parent():
    issues = vp.check_parents(
        [
            item("ES-1", parent=None, moscow="Must"),
            item("MRD-1", parent="ES-99", kano="basic"),
        ]
    )
    assert "BROKEN_PARENT" in error_codes(issues)


def test_level_skip():
    issues = vp.check_parents(
        [
            item("ES-3", parent=None, moscow="Must"),
            item("FRD-1", parent="ES-3", build="none", triad=triad()),
        ]
    )
    assert "LEVEL_SKIP" in error_codes(issues)


def test_numbering_gap():
    issues = vp.check_numbering(
        [
            item("ES-1", parent=None, moscow="Must"),
            item("ES-3", parent=None, moscow="Must"),
        ]
    )
    assert "NUMBERING" in error_codes(issues)


def test_reserved_ids_fill_numbering_gap():
    items = [
        item("ES-1", parent=None, moscow="Must"),
        item("ES-3", parent=None, moscow="Must"),
    ]
    assert "NUMBERING" in error_codes(vp.check_numbering(items))
    assert error_codes(vp.check_numbering(items, {"exec-summary": [2]})) == set()


def test_reserved_nested_slots():
    items = [
        item("PRD-1", parent="BRD-1", kind="container", spec="draft"),
        item("PRD-1.1", parent="PRD-1", moscow="Must"),
        item("PRD-1.3", parent="PRD-1", moscow="Must"),
    ]
    assert "NUMBERING" in error_codes(vp.check_numbering(items))
    assert error_codes(vp.check_numbering(items, {"prd": ["1.2"]})) == set()


def test_depth_three_rejected():
    issues = vp.check_unique_and_ids(
        [
            item(
                "PRD-1.2.3",
                title="too deep",
                parent="PRD-1.2",
                spec="idea",
            )
        ]
    )
    assert "INVALID_ID" in error_codes(issues)


def test_leaf_with_children():
    issues = vp.check_kind_and_children(
        [
            item("ES-1", parent=None, spec="draft"),
            item("ES-1.1", parent="ES-1", spec="draft", moscow="Must"),
        ]
    )
    assert "KIND" in error_codes(issues)


def test_container_without_children():
    issues = vp.check_kind_and_children(
        [item("ES-1", parent=None, kind="container", spec="draft")]
    )
    assert "KIND" in error_codes(issues)


def test_cycle():
    issues = vp.check_parents([item("PRD-1", parent="PRD-1", moscow="Must")])
    assert "CYCLE" in error_codes(issues) or "PARENT_SHAPE" in error_codes(issues)


def test_nested_parent_shape():
    issues = vp.check_parents(
        [
            item("PRD-1", parent="BRD-1", kind="container", spec="draft"),
            item("PRD-1.1", parent="BRD-1", moscow="Must"),
        ]
    )
    assert "PARENT_SHAPE" in error_codes(issues)


def test_duplicate_id():
    issues = vp.check_unique_and_ids(
        [
            item("ES-1", parent=None, spec="idea"),
            item("ES-1", parent=None, spec="idea", title="Again"),
        ]
    )
    assert "DUPLICATE_ID" in error_codes(issues)


def test_supersede_dangling():
    issues = vp.check_parents(
        [
            item(
                "FRD-1.1",
                parent="FRD-1",
                spec="deprecated",
                build="none",
                triad=triad(),
                superseded_by="FRD-9",
            )
        ]
    )
    assert "BROKEN_SUPERSEDE" in error_codes(issues)


def test_md_json_drift():
    md = [item("ES-1", parent=None, moscow="Must", title="Competitive window")]
    row = md[0].to_record()
    row["moscow"] = "Could"
    issues = vp.check_drift(md, [row])
    assert "DRIFT" in error_codes(issues)
