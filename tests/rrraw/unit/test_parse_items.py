"""Parser and closed-vocabulary tests."""

from __future__ import annotations

from pathlib import Path

import validate_planning as vp
from helpers import VALID_FILES, error_codes, write_planning


def test_parse_valid_headings():
    items, issues = vp.parse_markdown(VALID_FILES["prd.md"], "prd.md")
    assert not error_codes(issues)
    by_id = {item.id: item for item in items}
    assert by_id["PRD-1"].kind == "container"
    assert by_id["PRD-1"].parent == "BRD-1"
    assert by_id["PRD-1.1"].kind == "leaf"
    assert by_id["PRD-1.1"].moscow == "Must"
    assert by_id["PRD-1.1"].spec == "ready"


def test_parse_unranked_em_dash():
    items, _ = vp.parse_markdown(VALID_FILES["exec-summary.md"], "exec-summary.md")
    vision = next(item for item in items if item.id == "ES-1")
    assert vision.parent is None
    assert vision.moscow is None


def test_parse_triad_axis():
    items, issues = vp.parse_markdown(VALID_FILES["frd.md"], "frd.md")
    assert not error_codes(issues)
    leaf = next(item for item in items if item.id == "FRD-1.1")
    assert leaf.build == "in_progress"
    assert leaf.triad is not None
    assert leaf.triad.if_wrong.magnitude == "critical"
    assert leaf.triad.class_name == "must-correct"


def test_unknown_metadata_key(tmp_path: Path):
    files = {"exec-summary.md": """\
## ES-1: Vision
- **Parent:** —
- **Kind:** leaf
- **Spec:** idea
- **MoSCoW:** —
- **Priority:** P0
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "UNKNOWN_KEY" in error_codes(issues)


def test_missing_required_key(tmp_path: Path):
    files = {"exec-summary.md": """\
## ES-1: Vision
- **Kind:** leaf
- **Spec:** idea
- **MoSCoW:** —
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "MISSING_KEY" in error_codes(issues)


def test_malformed_meta_line(tmp_path: Path):
    files = {"exec-summary.md": """\
## ES-1: Vision
Parent: none
- **Kind:** leaf
- **Spec:** idea
- **MoSCoW:** —
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "MALFORMED_META" in error_codes(issues)
