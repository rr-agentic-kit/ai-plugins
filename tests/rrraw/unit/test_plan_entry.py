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
