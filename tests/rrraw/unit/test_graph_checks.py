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
## MRD-1: SMB buyers
- **Parent:** ES-99
- **Kind:** leaf
- **Spec:** ready
- **Kano:** —
"""
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "BROKEN_PARENT" in error_codes(issues)


def test_level_skip(tmp_path: Path):
    files = dict(VALID_FILES)
    files["frd.md"] = """\
## FRD-1: Guest checkout without account
- **Parent:** ES-3
- **Kind:** leaf
- **Spec:** ready
- **Build:** none
- **If present:** high — Unlocks conversion
- **If absent:** high — PLG blocked
- **If wrong:** low — Local defect
- **Class:** must-present
"""
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "LEVEL_SKIP" in error_codes(issues)


def test_numbering_gap(tmp_path: Path):
    files = {"exec-summary.md": """\
## ES-1: Vision
- **Parent:** —
- **Kind:** leaf
- **Spec:** ready
- **MoSCoW:** —

## ES-3: Metric
- **Parent:** —
- **Kind:** leaf
- **Spec:** ready
- **MoSCoW:** Must
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
- **Parent:** —
- **Kind:** leaf
- **Spec:** draft
- **MoSCoW:** —

### ES-1.1: Nested claim
- **Parent:** ES-1
- **Kind:** leaf
- **Spec:** draft
- **MoSCoW:** Must
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "KIND" in error_codes(issues)


def test_container_without_children(tmp_path: Path):
    files = {"exec-summary.md": """\
## ES-1: Vision
- **Parent:** —
- **Kind:** container
- **Spec:** draft
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "KIND" in error_codes(issues)


def test_cycle(tmp_path: Path):
    files = {"prd.md": """\
## PRD-1: A
- **Parent:** PRD-1
- **Kind:** leaf
- **Spec:** draft
- **MoSCoW:** Must
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "CYCLE" in error_codes(issues) or "PARENT_SHAPE" in error_codes(issues)


def test_nested_parent_shape(tmp_path: Path):
    files = dict(VALID_FILES)
    files["prd.md"] = """\
## PRD-1: Checkout
- **Parent:** BRD-1
- **Kind:** container
- **Spec:** draft

### PRD-1.1: Guest checkout
- **Parent:** BRD-1
- **Kind:** leaf
- **Spec:** ready
- **MoSCoW:** Must
"""
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "PARENT_SHAPE" in error_codes(issues)


def test_duplicate_id(tmp_path: Path):
    files = {"exec-summary.md": """\
## ES-1: Vision
- **Parent:** —
- **Kind:** leaf
- **Spec:** idea
- **MoSCoW:** —

## ES-1: Again
- **Parent:** —
- **Kind:** leaf
- **Spec:** idea
- **MoSCoW:** —
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "DUPLICATE_ID" in error_codes(issues)


def test_supersede_dangling(tmp_path: Path):
    files = dict(VALID_FILES)
    files["frd.md"] = """\
## FRD-1: Checkout
- **Parent:** PRD-1.1
- **Kind:** container
- **Spec:** draft

### FRD-1.1: Guest checkout without account
- **Parent:** FRD-1
- **Kind:** leaf
- **Spec:** deprecated
- **Build:** none
- **If present:** high — Unlocks conversion
- **If absent:** high — PLG blocked
- **If wrong:** critical — Billing disputes
- **Class:** must-correct
- **Superseded-by:** FRD-9
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
