"""validate_dir orchestrator wiring (tmp_path)."""

from __future__ import annotations

import json
from pathlib import Path

import validate_planning_script as vp
from helpers import (
    VALID_YAML_FILES,
    codes,
    error_codes,
    frozen_status,
    planning_items,
    write_planning,
)


def test_valid_cascade_passes(tmp_path: Path):
    write_planning(tmp_path)
    issues = vp.validate_dir(tmp_path)
    assert error_codes(issues) == set(), [i.format() for i in issues]


def test_live_yaml_is_stale_format(tmp_path: Path):
    write_planning(tmp_path, VALID_YAML_FILES)
    issues = vp.validate_dir(tmp_path)
    assert "STALE_FORMAT" in error_codes(issues)


def test_format_yaml_rejected(tmp_path: Path):
    write_planning(tmp_path)
    issues = vp.validate_dir(tmp_path, doc_format="yaml")
    assert "UNSUPPORTED_FORMAT" in error_codes(issues)


def test_unsupported_format_json(tmp_path: Path):
    write_planning(tmp_path)
    issues = vp.validate_dir(tmp_path, doc_format="json")
    assert "UNSUPPORTED_FORMAT" in error_codes(issues)


def test_sniff_yaml_is_stale(tmp_path: Path):
    write_planning(tmp_path, VALID_YAML_FILES)
    fmt, issues = vp.detect_doc_format(tmp_path)
    assert fmt is None
    assert "STALE_FORMAT" in error_codes(issues)


def test_missing_items_json(tmp_path: Path):
    write_planning(tmp_path, write_json=False)
    issues = vp.validate_dir(tmp_path)
    assert "MISSING_JSON" in error_codes(issues)


def test_extra_json_key(tmp_path: Path):
    write_planning(tmp_path)
    payload = json.loads((tmp_path / "items.json").read_text(encoding="utf-8"))
    payload["items"][0]["traces_to"] = "ES-1"
    (tmp_path / "items.json").write_text(json.dumps(payload), encoding="utf-8")
    issues = vp.validate_dir(tmp_path)
    assert "UNKNOWN_KEY" in error_codes(issues)


def test_future_md_ignored(tmp_path: Path):
    write_planning(tmp_path)
    bogus = """\
## ES-99: Bogus inbox item
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must
"""
    (tmp_path / vp.FUTURE_NAME).write_text(bogus, encoding="utf-8")
    (tmp_path / vp.AGENT_PLAN_NAME).write_text(bogus, encoding="utf-8")
    issues = vp.validate_dir(tmp_path)
    assert error_codes(issues) == set(), [i.format() for i in issues]
    assert not any(issue.item_id == "ES-99" for issue in issues)


def test_missing_status_yaml_skips_baseline_codes(tmp_path: Path):
    write_planning(tmp_path)
    issues = vp.validate_dir(tmp_path)
    assert error_codes(issues) == set(), [i.format() for i in issues]
    assert "HAND_BUMP" not in codes(issues)
    assert "STALE_PIN" not in codes(issues)


def test_challenge_dirty_is_not_script_fail(tmp_path: Path) -> None:
    write_planning(tmp_path)
    items = planning_items(tmp_path)
    status = frozen_status(items)
    status["challenge"] = {"prd": {"status": "dirty", "scanned_digest": "sha256:old"}}
    write_planning(tmp_path, status=status)
    issues = vp.validate_dir(tmp_path)
    assert error_codes(issues) == set(), [i.format() for i in issues]


def test_valid_rationale_round_trip_md(tmp_path: Path):
    from helpers import RATIONALE_FILES, VALID_LEDGER

    write_planning(tmp_path, RATIONALE_FILES, ledger=VALID_LEDGER)
    issues = vp.validate_dir(tmp_path)
    assert error_codes(issues) == set(), [i.format() for i in issues]
    items, _ = vp.parse_planning_dir(tmp_path)
    by_id = {item.id: item for item in items}
    assert by_id["PRD-1.1"].rationale == "r-004"
    assert "rationale" not in by_id["PRD-1"].to_record()
