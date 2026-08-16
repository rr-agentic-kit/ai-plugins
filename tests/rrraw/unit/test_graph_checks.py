"""Graph, numbering, and parent-walk tests."""

from __future__ import annotations

from pathlib import Path

import validate_planning as vp
from helpers import VALID_FILES, error_codes, write_planning


def test_valid_cascade_passes(tmp_path: Path):
    write_planning(tmp_path)
    issues = vp.validate_dir(tmp_path)
    assert error_codes(issues) == set(), [i.format() for i in issues]


def test_broken_parent(tmp_path: Path):
    files = dict(VALID_FILES)
    files["mrd.md"] = """\
## MRD-1: Account-free purchase
_parent_: ES-99 | _kind_: leaf | _spec_: ready | _kano_: basic
"""
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "BROKEN_PARENT" in error_codes(issues)


def test_level_skip(tmp_path: Path):
    files = dict(VALID_FILES)
    files["frd.md"] = """\
## FRD-1: Guest checkout without account
_parent_: ES-3 | _kind_: leaf | _spec_: ready | _build_: none | _if-present_: high — Unlocks conversion | _if-absent_: high — PLG blocked | _if-wrong_: low — Local defect | _class_: must-present
"""
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "LEVEL_SKIP" in error_codes(issues)


def test_numbering_gap(tmp_path: Path):
    files = {"exec-summary.md": """\
## ES-1: Competitive window
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must

## ES-3: Metric
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "NUMBERING" in error_codes(issues)


def test_depth_three_rejected():
    issues = vp.check_unique_and_ids(
        [
            vp.Item(
                id="PRD-1.2.3",
                title="too deep",
                prefix="PRD",
                doc="prd",
                parent="PRD-1.2",
                kind="leaf",
                spec="idea",
            )
        ]
    )
    assert "INVALID_ID" in error_codes(issues)


def test_leaf_with_children(tmp_path: Path):
    files = {"exec-summary.md": """\
## ES-1: Vision
_parent_: — | _kind_: leaf | _spec_: draft | _moscow_: —

### ES-1.1: Nested claim
_parent_: ES-1 | _kind_: leaf | _spec_: draft | _moscow_: Must
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "KIND" in error_codes(issues)


def test_container_without_children(tmp_path: Path):
    files = {"exec-summary.md": """\
## ES-1: Vision
_parent_: — | _kind_: container | _spec_: draft
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "KIND" in error_codes(issues)


def test_cycle(tmp_path: Path):
    files = {"prd.md": """\
## PRD-1: A
_parent_: PRD-1 | _kind_: leaf | _spec_: draft | _moscow_: Must
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "CYCLE" in error_codes(issues) or "PARENT_SHAPE" in error_codes(issues)


def test_nested_parent_shape(tmp_path: Path):
    files = dict(VALID_FILES)
    files["prd.md"] = """\
## PRD-1: Checkout
_parent_: BRD-1 | _kind_: container | _spec_: draft

### PRD-1.1: Guest checkout
_parent_: BRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Must
"""
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "PARENT_SHAPE" in error_codes(issues)


def test_duplicate_id(tmp_path: Path):
    files = {"exec-summary.md": """\
## ES-1: Vision
_parent_: — | _kind_: leaf | _spec_: idea | _moscow_: —

## ES-1: Again
_parent_: — | _kind_: leaf | _spec_: idea | _moscow_: —
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "DUPLICATE_ID" in error_codes(issues)


def test_supersede_dangling(tmp_path: Path):
    files = dict(VALID_FILES)
    files["frd.md"] = """\
## FRD-1: Checkout
_parent_: PRD-1.1 | _kind_: container | _spec_: draft

### FRD-1.1: Guest checkout without account
_parent_: FRD-1 | _kind_: leaf | _spec_: deprecated | _build_: none | _if-present_: high — Unlocks conversion | _if-absent_: high — PLG blocked | _if-wrong_: critical — Billing disputes | _class_: must-correct | _superseded-by_: FRD-9
"""
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "BROKEN_SUPERSEDE" in error_codes(issues)


def test_md_json_drift(tmp_path: Path):
    write_planning(tmp_path)
    records = (tmp_path / "items.json").read_text(encoding="utf-8")
    mutated = records.replace('"Must"', '"Could"', 1)
    (tmp_path / "items.json").write_text(mutated, encoding="utf-8")
    issues = vp.validate_dir(tmp_path)
    assert "DRIFT" in error_codes(issues)
