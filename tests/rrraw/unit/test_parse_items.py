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


def test_pipe_in_triad_effect_does_not_split_keys():
    text = """\
## FRD-1: Checkout
_parent_: PRD-1.1 | _kind_: leaf | _spec_: ready | _build_: none | _if-present_: high — Unlocks A | B conversion | _if-absent_: high — PLG blocked | _if-wrong_: low — Local defect | _class_: must-present
"""
    items, issues = vp.parse_markdown(text, "frd.md")
    assert "MALFORMED_META" not in error_codes(issues)
    leaf = items[0]
    assert leaf.triad is not None
    assert leaf.triad.if_present.effect == "Unlocks A | B conversion"


def test_unknown_metadata_key(tmp_path: Path):
    files = {"exec-summary.md": """\
## ES-1: Vision
_parent_: — | _kind_: leaf | _spec_: idea | _moscow_: — | _priority_: P0
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "UNKNOWN_KEY" in error_codes(issues)


def test_missing_required_key(tmp_path: Path):
    files = {"exec-summary.md": """\
## ES-1: Vision
_kind_: leaf | _spec_: idea | _moscow_: —
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "MISSING_KEY" in error_codes(issues)


def test_malformed_meta_line(tmp_path: Path):
    files = {"exec-summary.md": """\
## ES-1: Vision
Parent: none
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "MALFORMED_META" in error_codes(issues)


def test_stale_list_meta(tmp_path: Path):
    files = {"exec-summary.md": """\
## ES-1: Vision
- **Parent:** —
- **Kind:** leaf
- **Spec:** idea
- **MoSCoW:** —
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "STALE_FORMAT" in error_codes(issues)


def test_body_not_blockquote(tmp_path: Path):
    files = {"exec-summary.md": """\
## ES-1: Vision
_parent_: — | _kind_: leaf | _spec_: idea | _moscow_: —

Vision without quotes.
"""}
    write_planning(tmp_path, files)
    issues = vp.validate_dir(tmp_path)
    assert "BODY_NOT_BLOCKQUOTE" in error_codes(issues)
