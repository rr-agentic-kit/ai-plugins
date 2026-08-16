"""Rationale closed key, decision-ledger.yaml, drift."""

from __future__ import annotations

import json
from pathlib import Path

import validate_planning as vp
from helpers import (
    RATIONALE_FILES,
    RATIONALE_YAML_FILES,
    VALID_LEDGER,
    codes,
    error_codes,
    write_planning,
)


def test_valid_rationale_round_trip_md(tmp_path: Path):
    write_planning(tmp_path, RATIONALE_FILES, ledger=VALID_LEDGER)
    issues = vp.validate_dir(tmp_path)
    assert error_codes(issues) == set(), [i.format() for i in issues]
    items, _ = vp.parse_planning_dir(tmp_path)
    by_id = {item.id: item for item in items}
    assert by_id["PRD-1.1"].rationale == "r-004"
    assert by_id["ES-1"].rationale is None
    record = by_id["PRD-1.1"].to_record()
    assert record["rationale"] == "r-004"
    assert "rationale" not in by_id["ES-1"].to_record()


def test_valid_rationale_round_trip_yaml_rewrite(tmp_path: Path):
    write_planning(tmp_path, RATIONALE_YAML_FILES, ledger=VALID_LEDGER)
    assert vp.main([str(tmp_path), "--rewrite"]) == 0
    issues = vp.validate_dir(tmp_path)
    assert error_codes(issues) == set(), [i.format() for i in issues]
    items, _ = vp.parse_planning_dir(tmp_path)
    by_id = {item.id: item for item in items}
    assert by_id["FRD-1.1"].rationale == "r-005"
    assert by_id["PRD-1"].rationale is None


def test_missing_rationale_on_ranked_leaf(tmp_path: Path):
    files = dict(RATIONALE_FILES)
    files["prd.md"] = """\
## PRD-1: Checkout
_parent_: BRD-1 | _kind_: container | _spec_: draft

### PRD-1.1: Guest checkout
_parent_: PRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Must

> As a guest, I can complete checkout without an account.
"""
    write_planning(tmp_path, files, ledger=VALID_LEDGER)
    issues = vp.validate_dir(tmp_path)
    assert "MISSING_RATIONALE" in error_codes(issues)


def test_dangling_rationale_id(tmp_path: Path):
    files = dict(RATIONALE_FILES)
    files["prd.md"] = """\
## PRD-1: Checkout
_parent_: BRD-1 | _kind_: container | _spec_: draft

### PRD-1.1: Guest checkout
_parent_: PRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Must | _rationale_: r-999

> As a guest, I can complete checkout without an account.
"""
    write_planning(tmp_path, files, ledger=VALID_LEDGER)
    issues = vp.validate_dir(tmp_path)
    assert "BROKEN_RATIONALE" in error_codes(issues)


def test_malformed_ledger(tmp_path: Path):
    write_planning(tmp_path, RATIONALE_FILES, ledger="just a string\n")
    issues = vp.validate_dir(tmp_path)
    assert "LEDGER_MALFORMED" in error_codes(issues)


def test_malformed_ledger_missing_flips_when(tmp_path: Path):
    ledger = """\
version: 1
evidence: {}
rationales:
  r-001:
    decision: accept
    subject: ES-3
    seat: seed-investor
    because: "no flips"
    depends_on: []
    flips_when: []
    condition_strength: vague
    status: live
"""
    write_planning(tmp_path, RATIONALE_FILES, ledger=ledger)
    issues = vp.validate_dir(tmp_path)
    assert "LEDGER_MALFORMED" in error_codes(issues)


def test_missing_ledger_is_warning(tmp_path: Path):
    write_planning(tmp_path)
    issues = vp.validate_dir(tmp_path)
    assert "LEDGER_MISSING" in codes(issues)
    assert "LEDGER_MISSING" not in error_codes(issues)
    assert "MISSING_RATIONALE" not in error_codes(issues)
    assert error_codes(issues) == set(), [i.format() for i in issues]


def test_rationale_key_drift(tmp_path: Path):
    write_planning(tmp_path, RATIONALE_FILES, ledger=VALID_LEDGER)
    payload = json.loads((tmp_path / "items.json").read_text(encoding="utf-8"))
    for row in payload["items"]:
        if row.get("id") == "PRD-1.1":
            row["rationale"] = "r-001"
    (tmp_path / "items.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    issues = vp.validate_dir(tmp_path)
    assert "DRIFT" in error_codes(issues)


def test_invalid_rationale_shape(tmp_path: Path):
    files = dict(RATIONALE_FILES)
    files["prd.md"] = """\
## PRD-1: Checkout
_parent_: BRD-1 | _kind_: container | _spec_: draft

### PRD-1.1: Guest checkout
_parent_: PRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Must | _rationale_: rationale-4

> As a guest, I can complete checkout without an account.
"""
    write_planning(tmp_path, files, ledger=VALID_LEDGER)
    issues = vp.validate_dir(tmp_path)
    assert "INVALID_VALUE" in error_codes(issues)
