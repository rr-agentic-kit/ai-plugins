"""Rationale closed key, ledger shape, drift (in-memory)."""

from __future__ import annotations

from pathlib import Path

import validate_planning_script as vp
import yaml
from helpers import VALID_LEDGER, codes, error_codes, item, prd_rice
from validate_planning_script.ledger import check_ledger_shape


def _ledger() -> dict:
    data = yaml.safe_load(VALID_LEDGER)
    assert isinstance(data, dict)
    return data


def test_missing_rationale_on_ranked_leaf():
    issues = vp.check_rationale(
        [
            item("PRD-1", parent="BRD-1", kind="container", spec="draft"),
            prd_rice("PRD-1.1", parent="PRD-1"),
        ],
        _ledger(),
    )
    assert "MISSING_RATIONALE" in error_codes(issues)


def test_dangling_rationale_id():
    issues = vp.check_rationale(
        [prd_rice("PRD-1.1", parent="PRD-1", rationale="r-999")],
        _ledger(),
    )
    assert "BROKEN_RATIONALE" in error_codes(issues)


def test_valid_rationale_on_ranked_leaf():
    issues = vp.check_rationale(
        [prd_rice("PRD-1.1", parent="PRD-1", rationale="r-004")],
        _ledger(),
    )
    assert error_codes(issues) == set()


def test_container_skips_rationale():
    issues = vp.check_rationale(
        [item("PRD-1", parent="BRD-1", kind="container", spec="draft")],
        _ledger(),
    )
    assert error_codes(issues) == set()


def test_malformed_ledger_not_mapping(tmp_path: Path):
    path = tmp_path / "decision-ledger.yaml"
    path.write_text("just a string\n", encoding="utf-8")
    ledger, issues = vp.load_ledger(path)
    assert ledger is None
    assert "LEDGER_MALFORMED" in error_codes(issues)


def test_malformed_ledger_missing_flips_when():
    issues = check_ledger_shape(
        {
            "evidence": {},
            "rationales": {
                "r-001": {
                    "decision": "accept",
                    "subject": "ES-3",
                    "flips_when": [],
                    "status": "live",
                }
            },
        }
    )
    assert "LEDGER_MALFORMED" in error_codes(issues)


def test_missing_ledger_is_warning():
    ledger, issues = vp.load_ledger(Path("/no/such/decision-ledger.yaml"))
    assert ledger is None
    assert "LEDGER_MISSING" in codes(issues)
    assert "LEDGER_MISSING" not in error_codes(issues)
    ranked = [item("ES-1", parent=None, moscow="Must")]
    assert "MISSING_RATIONALE" not in error_codes(vp.check_rationale(ranked, None))


def test_rationale_key_drift():
    md = [prd_rice("PRD-1.1", parent="PRD-1", rationale="r-004")]
    row = md[0].to_record()
    row["rationale"] = "r-001"
    issues = vp.check_drift(md, [row])
    assert "DRIFT" in error_codes(issues)


def test_ledger_evidence_shape_branches():
    issues = check_ledger_shape({"evidence": [], "rationales": {}})
    assert "LEDGER_MALFORMED" in error_codes(issues)
    issues = check_ledger_shape(
        {"evidence": {"nope": {"status": "supported"}}, "rationales": {}}
    )
    assert "LEDGER_MALFORMED" in error_codes(issues)
    issues = check_ledger_shape({"evidence": {"e-001": "x"}, "rationales": {}})
    assert "LEDGER_MALFORMED" in error_codes(issues)
    issues = check_ledger_shape(
        {"evidence": {"e-001": {"status": "bogus"}}, "rationales": {}}
    )
    assert "LEDGER_MALFORMED" in error_codes(issues)


def test_ledger_rationale_and_queue_shape_branches():
    issues = check_ledger_shape({"rationales": []})
    assert "LEDGER_MALFORMED" in error_codes(issues)
    issues = check_ledger_shape({"rationales": {"nope": {}}})
    assert "LEDGER_MALFORMED" in error_codes(issues)
    issues = check_ledger_shape({"rationales": {"r-001": "x"}})
    assert "LEDGER_MALFORMED" in error_codes(issues)
    issues = check_ledger_shape(
        {
            "evidence": {},
            "rationales": {
                "r-001": {
                    "decision": "accept",
                    "status": "live",
                    "flips_when": [{"kind": "fact", "evidence": "e-999"}],
                }
            },
        }
    )
    assert "BROKEN_RATIONALE" in error_codes(issues)
    issues = check_ledger_shape(
        {
            "rationales": {
                "r-001": {
                    "decision": "accept",
                    "status": "live",
                    "flips_when": [{"kind": "metric", "metric": "x", "op": "<"}],
                }
            }
        }
    )
    assert "LEDGER_MALFORMED" in error_codes(issues)
    issues = check_ledger_shape(
        {
            "rationales": {
                "r-001": {
                    "decision": "accept",
                    "status": "live",
                    "flips_when": [{"kind": "event", "text": ""}],
                }
            }
        }
    )
    assert "LEDGER_MALFORMED" in error_codes(issues)
    issues = check_ledger_shape(
        {
            "rationales": {},
            "graveyard": [],
            "reserved_ids": [],
            "re_decision_queue": [{"status": "bogus", "rationale": "r-001"}],
        }
    )
    codes_found = error_codes(issues)
    assert "LEDGER_MALFORMED" in codes_found
    assert "BROKEN_RATIONALE" in codes_found
