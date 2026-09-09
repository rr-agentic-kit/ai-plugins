"""Discovery-only validate + Plan entry gate (business-case handoff)."""

from __future__ import annotations

from pathlib import Path

import validate_planning_script as vp
import yaml
from helpers import VALID_FILES, error_codes, write_planning

MINIMAL_BUSINESS_CASE: dict = {
    "track": "0.1",
    "docs": "0.1.1",
    "product": "0.1.0?",
    "vision": "Self-serve checkout without accounts",
    "problem": "Guests abandon when forced to register",
    "premises": [
        {
            "id": "P1",
            "text": "Guests will pay",
            "claim_class": "assumption",
            "status": "open",
        }
    ],
    "viability_verdict": "proceed",
    "north_star": "Guest checkout completion rate",
    "input_metrics": ["guest session → payment start"],
    "cost_position": "unique-value",
    "defensibility": "Can't: payment vault; Won't: force account",
    "market_read": "Mid-market ecommerce; incumbent forces accounts; do-nothing = abandon",
    "beachhead_icp": "SMB storefronts; why first: highest abandon; JTBD: buy fast",
    "objectives": ["Increase self-serve revenue"],
    "stakeholders": [
        {
            "role": "buyer",
            "name_or_title": "Merch lead",
            "power": "high",
            "interest": "high",
            "grid": "manage_closely",
        }
    ],
    "capabilities": [{"choice": "build", "what": "guest checkout"}],
    "constraints": ["PCI scope"],
    "non_goals": ["Loyalty rewrite"],
    "gtm_motion": "plg",
    "open_holds": [],
    "artifact_refs": {},
    "ledger_pins": [],
}


def test_discovery_only_dir_validates_without_prd(tmp_path: Path) -> None:
    discovery = {
        "executive-summary.md": VALID_FILES["executive-summary.md"],
        "mrd.md": VALID_FILES["mrd.md"],
        "brd.md": VALID_FILES["brd.md"],
    }
    write_planning(tmp_path, discovery)
    issues = vp.validate_dir(tmp_path)
    assert error_codes(issues) == set()
    assert not vp.has_prd_doc(tmp_path)


def test_plan_entry_refuses_without_frozen_brd_or_handoff(tmp_path: Path) -> None:
    write_planning(tmp_path, VALID_FILES)
    issues = vp.check_plan_entry(tmp_path)
    codes = error_codes(issues)
    assert "PLAN_ENTRY_BRD" in codes
    assert "MISSING_BUSINESS_CASE" in codes


def test_plan_entry_passes_with_frozen_brd_and_business_case(tmp_path: Path) -> None:
    write_planning(
        tmp_path,
        VALID_FILES,
        session={"frozen_levels": ["executive-summary", "mrd", "brd"]},
    )
    (tmp_path / vp.BUSINESS_CASE_NAME).write_text(
        yaml.safe_dump(MINIMAL_BUSINESS_CASE, sort_keys=False),
        encoding="utf-8",
    )
    issues = vp.check_plan_entry(tmp_path)
    assert error_codes(issues) == set()


def test_validate_dir_require_plan_entry_flag(tmp_path: Path) -> None:
    write_planning(tmp_path, VALID_FILES)
    issues = vp.validate_dir(tmp_path, require_plan_entry=True)
    assert "PLAN_ENTRY_BRD" in error_codes(
        issues
    ) or "MISSING_BUSINESS_CASE" in error_codes(issues)


def test_business_case_missing_fields(tmp_path: Path) -> None:
    write_planning(
        tmp_path,
        VALID_FILES,
        session={"frozen_levels": ["brd"]},
    )
    (tmp_path / vp.BUSINESS_CASE_NAME).write_text(
        "vision: only\n",
        encoding="utf-8",
    )
    issues = vp.check_business_case(tmp_path)
    assert "BUSINESS_CASE_FIELDS" in error_codes(issues)


MINIMAL_EXECUTE_SLICE: dict = {
    "track": "0.1",
    "docs": "0.1.7",
    "product": "0.1.0?",
    "slice_id": "slice-001",
    "why": "Guest checkout without account friction",
    "capabilities": ["Guest may pay without account"],
    "constraints": ["PCI vault via existing payment adapter (deltas/PRD-3.md)"],
    "non_goals": ["Loyalty rewrite"],
    "success_signal": "Guest completes payment without creating an account",
    "pins": {
        "requirement_ids": ["PRD-3.1"],
        "parents": ["PRD-3"],
        "delta_paths": ["deltas/PRD-3.md"],
        "architecture_rev": "draft",
        "ac_refs": ["prd.md § Guest checkout AC"],
    },
}


def test_execute_slice_absent_is_ok(tmp_path: Path) -> None:
    write_planning(tmp_path, VALID_FILES)
    assert error_codes(vp.check_execute_slice(tmp_path)) == set()


def test_execute_slice_missing_fields(tmp_path: Path) -> None:
    write_planning(tmp_path, VALID_FILES)
    (tmp_path / vp.EXECUTE_SLICE_NAME).write_text("why: only\n", encoding="utf-8")
    issues = vp.check_execute_slice(tmp_path)
    assert "EXECUTE_SLICE_FIELDS" in error_codes(issues)


def test_execute_slice_missing_delta_file(tmp_path: Path) -> None:
    write_planning(tmp_path, VALID_FILES)
    (tmp_path / vp.EXECUTE_SLICE_NAME).write_text(
        yaml.safe_dump(MINIMAL_EXECUTE_SLICE, sort_keys=False),
        encoding="utf-8",
    )
    issues = vp.check_execute_slice(tmp_path)
    assert "EXECUTE_SLICE_DELTA_PATH" in error_codes(issues)


def test_execute_slice_passes_with_delta_file(tmp_path: Path) -> None:
    write_planning(tmp_path, VALID_FILES)
    deltas = tmp_path / "deltas"
    deltas.mkdir()
    (deltas / "PRD-3.md").write_text("# delta\n", encoding="utf-8")
    (tmp_path / vp.EXECUTE_SLICE_NAME).write_text(
        yaml.safe_dump(MINIMAL_EXECUTE_SLICE, sort_keys=False),
        encoding="utf-8",
    )
    assert error_codes(vp.check_execute_slice(tmp_path)) == set()


def test_execute_slice_rejects_path_escape(tmp_path: Path) -> None:
    write_planning(tmp_path, VALID_FILES)
    bad = dict(MINIMAL_EXECUTE_SLICE)
    bad["pins"] = dict(MINIMAL_EXECUTE_SLICE["pins"])
    bad["pins"]["delta_paths"] = ["../secret.md"]
    (tmp_path / vp.EXECUTE_SLICE_NAME).write_text(
        yaml.safe_dump(bad, sort_keys=False),
        encoding="utf-8",
    )
    issues = vp.check_execute_slice(tmp_path)
    assert "EXECUTE_SLICE_DELTA_PATH" in error_codes(issues)
