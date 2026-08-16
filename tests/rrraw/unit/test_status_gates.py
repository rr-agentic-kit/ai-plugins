"""Spec/build DoR gates, class derivation, deprecate/supersede."""

from __future__ import annotations

from pathlib import Path

import validate_planning as vp
from helpers import VALID_FILES, codes, error_codes, write_planning


def test_derived_class_partition():
    assert vp.derived_class("high", "high", "critical") == "must-correct"
    assert vp.derived_class("low", "high", "low") == "must-present"
    assert vp.derived_class("low", "low", "high") == "protect"
    assert vp.derived_class("high", "low", "low") == "leverage"
    assert vp.derived_class("low", "low", "low") == "optional"
    assert vp.derived_class("high", "moderate", "low") == "optional"


def test_class_mismatch(tmp_path: Path):
    files = dict(VALID_FILES)
    files["frd.md"] = """\
## FRD-1: Checkout
_parent_: PRD-1.1 | _kind_: container | _spec_: draft

### FRD-1.1: Guest checkout without account
_parent_: FRD-1 | _kind_: leaf | _spec_: ready | _build_: none | _if-present_: high — Unlocks conversion | _if-absent_: high — PLG blocked | _if-wrong_: critical — Billing disputes | _class_: optional
"""
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "CLASS_MISMATCH" in error_codes(issues)


def test_build_on_draft_fails(tmp_path: Path):
    files = dict(VALID_FILES)
    files["frd.md"] = """\
## FRD-1: Checkout
_parent_: PRD-1.1 | _kind_: container | _spec_: draft

### FRD-1.1: Guest checkout without account
_parent_: FRD-1 | _kind_: leaf | _spec_: draft | _build_: in_progress | _if-present_: high — Unlocks conversion | _if-absent_: high — PLG blocked | _if-wrong_: low — Local defect | _class_: must-present
"""
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "BUILD_GATE" in error_codes(issues)


def test_build_on_prd_fails(tmp_path: Path):
    files = dict(VALID_FILES)
    files["prd.md"] = """\
## PRD-1: Checkout
_parent_: BRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Must | _build_: done
"""
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "BUILD_SCOPE" in error_codes(issues)


def test_ready_cross_doc_parent_must_be_ready(tmp_path: Path):
    files = dict(VALID_FILES)
    files["brd.md"] = """\
## BRD-1: Increase self-serve revenue
_parent_: MRD-2 | _kind_: leaf | _spec_: draft | _moscow_: Must
"""
    files["prd.md"] = """\
## PRD-1: Checkout
_parent_: BRD-1 | _kind_: container | _spec_: ready

### PRD-1.1: Guest checkout
_parent_: PRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Must

> As a guest, I can complete checkout without an account.
"""
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "PARENT_READY" in error_codes(issues)


def test_same_doc_container_draft_child_ready_ok(tmp_path: Path):
    write_planning(tmp_path)
    issues = vp.validate_dir(tmp_path)
    assert "PARENT_READY" not in error_codes(issues)
    assert error_codes(issues) == set(), [i.format() for i in issues]


def test_idea_with_children_fails(tmp_path: Path):
    files = {"exec-summary.md": """\
## ES-1: Vision
_parent_: — | _kind_: container | _spec_: idea

### ES-1.1: Nested
_parent_: ES-1 | _kind_: leaf | _spec_: idea | _moscow_: —
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "IDEA_CHILDREN" in error_codes(issues)


def test_deprecated_in_progress_warns(tmp_path: Path):
    files = dict(VALID_FILES)
    files["frd.md"] = """\
## FRD-1: Checkout
_parent_: PRD-1.1 | _kind_: container | _spec_: draft

### FRD-1.1: Guest checkout without account
_parent_: FRD-1 | _kind_: leaf | _spec_: deprecated | _build_: in_progress | _if-present_: high — Unlocks conversion | _if-absent_: high — PLG blocked | _if-wrong_: critical — Billing disputes | _class_: must-correct
"""
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "DEPRECATED_BUILD" in codes(issues)
    assert "DEPRECATED_BUILD" not in error_codes(issues)
    assert "BUILD_GATE" in error_codes(issues)


def test_supersede_pair(tmp_path: Path):
    files = dict(VALID_FILES)
    files["frd.md"] = """\
## FRD-1: Checkout
_parent_: PRD-1.1 | _kind_: container | _spec_: draft

### FRD-1.1: Old guest checkout
_parent_: FRD-1 | _kind_: leaf | _spec_: deprecated | _build_: none | _if-present_: high — Unlocks conversion | _if-absent_: high — PLG blocked | _if-wrong_: critical — Billing disputes | _class_: must-correct | _superseded-by_: FRD-2

## FRD-2: Replacement guest checkout
_parent_: PRD-1.1 | _kind_: leaf | _spec_: draft | _build_: none | _if-present_: high — Unlocks conversion | _if-absent_: high — PLG blocked | _if-wrong_: critical — Billing disputes | _class_: must-correct | _supersedes_: FRD-1.1
"""
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "BROKEN_SUPERSEDE" not in error_codes(issues)
    assert "SUPERSEDE_PAIR" not in error_codes(issues)


def test_revive_deprecated_fails(tmp_path: Path):
    write_planning(
        tmp_path,
        session={
            "item_registry": {
                "ES-1": {
                    "doc": "exec-summary",
                    "parent": None,
                    "kind": "leaf",
                    "spec": "deprecated",
                }
            }
        },
    )
    issues = vp.validate_dir(tmp_path)
    assert "REVIVE" in error_codes(issues)
