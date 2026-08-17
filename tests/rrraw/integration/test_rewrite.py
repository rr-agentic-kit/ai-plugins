"""Rewrite yaml/list-meta to canonical md (filesystem)."""

from __future__ import annotations

from pathlib import Path

import validate_planning_script as vp
from helpers import (
    RATIONALE_YAML_FILES,
    VALID_FILES,
    VALID_LEDGER,
    VALID_YAML_FILES,
    error_codes,
    write_planning,
)


def test_rewrite_yaml_to_md(tmp_path: Path):
    write_planning(tmp_path, VALID_YAML_FILES)
    assert vp.main([str(tmp_path), "--rewrite"]) == 0
    for stem in vp.DOC_STEMS:
        assert (tmp_path / f"{stem}.md").is_file()
        assert not (tmp_path / f"{stem}.yaml").exists()
    items, issues = vp.parse_planning_dir(tmp_path)
    assert not error_codes(issues)
    by_id = {item.id: item for item in items}
    assert by_id["PRD-1.1"].moscow == "Must"
    assert by_id["FRD-1.1"].triad is not None
    prd = (tmp_path / "prd.md").read_text(encoding="utf-8")
    assert "_parent_: PRD-1" in prd
    assert "> As a guest, I can complete checkout without an account." in prd


def test_rewrite_list_meta_to_inline(tmp_path: Path):
    files = {"exec-summary.md": """\
# Exec summary

## ES-1: Competitive window
- **Parent:** —
- **Kind:** leaf
- **Spec:** ready
- **MoSCoW:** Must

Why now.
"""}
    write_planning(tmp_path, files)
    assert vp.main([str(tmp_path), "--rewrite"]) == 0
    text = (tmp_path / "exec-summary.md").read_text(encoding="utf-8")
    assert "- **Parent:**" not in text
    assert "_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must" in text
    assert "> Why now." in text
    issues = vp.validate_dir(tmp_path)
    assert "STALE_FORMAT" not in error_codes(issues)
    assert error_codes(issues) == set(), [i.format() for i in issues]


def test_rewrite_does_not_inject_omitted_moscow(tmp_path: Path):
    files = {"exec-summary.md": """\
# Exec summary

## ES-1: Competitive window
_parent_: — | _kind_: leaf | _spec_: idea

> Why now, cut undecided.
"""}
    write_planning(tmp_path, files)
    assert vp.main([str(tmp_path), "--rewrite"]) == 0
    text = (tmp_path / "exec-summary.md").read_text(encoding="utf-8")
    assert "_moscow_:" not in text
    assert "_parent_: — | _kind_: leaf | _spec_: idea" in text
    issues = vp.validate_dir(tmp_path)
    assert "MISSING_KEY" not in error_codes(issues)
    assert "DOR" not in error_codes(issues)
    assert error_codes(issues) == set(), [i.format() for i in issues]


def test_rewrite_preserves_prose_headings(tmp_path: Path):
    files = {
        "exec-summary.md": """\
# Exec summary

## Vision

Guest checkout growth.

## ES-1: Self-serve conversion
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must

> Metric.
""",
        "mrd.md": """\
# MRD

## Target segments

**Primary:** SMB buyers.

## MRD-1: Account-free purchase
_parent_: ES-1 | _kind_: leaf | _spec_: ready | _kano_: basic
""",
        "brd.md": """\
# BRD

## Stakeholders

Buyer vs user vs approver.

## BRD-1: Increase self-serve revenue
_parent_: MRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Must
""",
        "prd.md": """\
# PRD

## User personas

Guest shopper.

## PRD-1: Guest checkout
_parent_: BRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Must

> As a guest, I can complete checkout without an account.
""",
        "frd.md": """\
# FRD

## FRD-1: Guest checkout without account
_parent_: PRD-1 | _kind_: leaf | _spec_: ready | _build_: none | _if-present_: high — Unlocks conversion | _if-absent_: high — PLG blocked | _if-wrong_: low — Local defect | _class_: must-present
""",
    }
    write_planning(tmp_path, files)
    assert vp.main([str(tmp_path), "--rewrite"]) == 0
    es = (tmp_path / "exec-summary.md").read_text(encoding="utf-8")
    mrd = (tmp_path / "mrd.md").read_text(encoding="utf-8")
    brd = (tmp_path / "brd.md").read_text(encoding="utf-8")
    prd = (tmp_path / "prd.md").read_text(encoding="utf-8")
    assert "## Vision" in es
    assert "## Target segments" in mrd
    assert "## Stakeholders" in brd
    assert "## User personas" in prd
    issues = vp.validate_dir(tmp_path)
    assert "STALE_FORMAT" not in error_codes(issues)
    assert error_codes(issues) == set(), [i.format() for i in issues]


def test_mixed_dir_rewrites_yaml_away(tmp_path: Path):
    write_planning(tmp_path, VALID_FILES)
    (tmp_path / "prd.yaml").write_text(VALID_YAML_FILES["prd.yaml"], encoding="utf-8")
    assert vp.main([str(tmp_path), "--rewrite"]) == 0
    assert not (tmp_path / "prd.yaml").exists()
    assert (tmp_path / "prd.md").is_file()
    issues = vp.validate_dir(tmp_path)
    assert "STALE_FORMAT" not in error_codes(issues)
    assert error_codes(issues) == set(), [i.format() for i in issues]


def test_rewrite_invalid_yaml_keeps_source(tmp_path: Path):
    files = {"exec-summary.yaml": "- just a list\n"}
    write_planning(tmp_path, files)
    assert vp.main([str(tmp_path), "--rewrite"]) == 1
    assert (tmp_path / "exec-summary.yaml").is_file()
    assert not (tmp_path / "exec-summary.md").exists()


def test_valid_rationale_round_trip_yaml_rewrite(tmp_path: Path):
    write_planning(tmp_path, RATIONALE_YAML_FILES, ledger=VALID_LEDGER)
    assert vp.main([str(tmp_path), "--rewrite"]) == 0
    issues = vp.validate_dir(tmp_path)
    assert error_codes(issues) == set(), [i.format() for i in issues]
    items, _ = vp.parse_planning_dir(tmp_path)
    by_id = {item.id: item for item in items}
    assert by_id["FRD-1.1"].rationale == "r-005"
    assert by_id["PRD-1"].rationale is None
