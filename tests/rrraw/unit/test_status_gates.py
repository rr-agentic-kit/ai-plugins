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
- **Parent:** PRD-1.1
- **Kind:** container
- **Spec:** draft

### FRD-1.1: Guest checkout without account
- **Parent:** FRD-1
- **Kind:** leaf
- **Spec:** ready
- **Build:** none
- **If present:** high — Unlocks conversion
- **If absent:** high — PLG blocked
- **If wrong:** critical — Billing disputes
- **Class:** optional
"""
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "CLASS_MISMATCH" in error_codes(issues)


def test_build_on_draft_fails(tmp_path: Path):
    files = dict(VALID_FILES)
    files["frd.md"] = """\
## FRD-1: Checkout
- **Parent:** PRD-1.1
- **Kind:** container
- **Spec:** draft

### FRD-1.1: Guest checkout without account
- **Parent:** FRD-1
- **Kind:** leaf
- **Spec:** draft
- **Build:** in_progress
- **If present:** high — Unlocks conversion
- **If absent:** high — PLG blocked
- **If wrong:** low — Local defect
- **Class:** must-present
"""
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "BUILD_GATE" in error_codes(issues)


def test_build_on_prd_fails(tmp_path: Path):
    files = dict(VALID_FILES)
    files["prd.md"] = """\
## PRD-1: Checkout
- **Parent:** BRD-1
- **Kind:** leaf
- **Spec:** ready
- **MoSCoW:** Must
- **Build:** done
"""
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "BUILD_SCOPE" in error_codes(issues)


def test_ready_cross_doc_parent_must_be_ready(tmp_path: Path):
    files = dict(VALID_FILES)
    files["brd.md"] = """\
## BRD-1: Increase self-serve revenue
- **Parent:** MRD-2
- **Kind:** leaf
- **Spec:** draft
- **MoSCoW:** Must
"""
    files["prd.md"] = """\
## PRD-1: Checkout
- **Parent:** BRD-1
- **Kind:** container
- **Spec:** ready

### PRD-1.1: Guest checkout
- **Parent:** PRD-1
- **Kind:** leaf
- **Spec:** ready
- **MoSCoW:** Must

As a guest, I can complete checkout without an account.
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
- **Parent:** —
- **Kind:** container
- **Spec:** idea

### ES-1.1: Nested
- **Parent:** ES-1
- **Kind:** leaf
- **Spec:** idea
- **MoSCoW:** —
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "IDEA_CHILDREN" in error_codes(issues)


def test_deprecated_in_progress_warns(tmp_path: Path):
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
- **Build:** in_progress
- **If present:** high — Unlocks conversion
- **If absent:** high — PLG blocked
- **If wrong:** critical — Billing disputes
- **Class:** must-correct
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
- **Parent:** PRD-1.1
- **Kind:** container
- **Spec:** draft

### FRD-1.1: Old guest checkout
- **Parent:** FRD-1
- **Kind:** leaf
- **Spec:** deprecated
- **Build:** none
- **If present:** high — Unlocks conversion
- **If absent:** high — PLG blocked
- **If wrong:** critical — Billing disputes
- **Class:** must-correct
- **Superseded-by:** FRD-2

## FRD-2: Replacement guest checkout
- **Parent:** PRD-1.1
- **Kind:** leaf
- **Spec:** draft
- **Build:** none
- **If present:** high — Unlocks conversion
- **If absent:** high — PLG blocked
- **If wrong:** critical — Billing disputes
- **Class:** must-correct
- **Supersedes:** FRD-1.1
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
