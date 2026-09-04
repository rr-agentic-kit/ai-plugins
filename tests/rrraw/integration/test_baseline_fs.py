"""Cascade baselines: status.yaml, agent.plan.md, pins (filesystem)."""

from __future__ import annotations

from pathlib import Path

import validate_planning_script as vp
from helpers import (
    VALID_FILES,
    codes,
    error_codes,
    frozen_status,
    planning_items,
    write_planning,
)


def test_emit_agent_plan(tmp_path: Path):
    path = vp.emit_agent_plan(tmp_path)
    assert path == tmp_path / "agent.plan.md"
    text = path.read_text(encoding="utf-8")
    assert text.startswith("# Planning pairing")
    assert "rrr-status.yaml" in text
    assert text.endswith("\n")
    vp.emit_agent_plan(tmp_path)
    assert path.read_text(encoding="utf-8") == text


def test_sync_one_liner_on_claude_and_agents(tmp_path: Path):
    _, load_line, _ = vp.parse_agent_config()
    (tmp_path / "CLAUDE.md").write_text("# Project\n\nBody stays.\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    updated = vp.sync_root_sot(tmp_path)
    assert {path.name for path in updated} == {"CLAUDE.md", "AGENTS.md"}
    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert load_line in claude
    assert load_line in agents
    assert claude.startswith("# Project\n\nBody stays.\n")
    assert vp.sync_root_sot(tmp_path) == []


def test_restore_one_liner_if_stripped(tmp_path: Path):
    _, load_line, _ = vp.parse_agent_config()
    (tmp_path / "CLAUDE.md").write_text("# Project\n\nBody stays.\n", encoding="utf-8")
    vp.sync_root_sot(tmp_path)
    (tmp_path / "CLAUDE.md").write_text("# Project\n\nBody stays.\n", encoding="utf-8")
    updated = vp.sync_root_sot(tmp_path)
    assert updated == [tmp_path / "CLAUDE.md"]
    text = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert load_line in text
    assert "Body stays." in text


def test_sync_does_not_create_missing_sot(tmp_path: Path):
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    vp.sync_root_sot(tmp_path)
    assert not (tmp_path / "AGENTS.md").exists()
    assert not (tmp_path / "GEMINI.md").exists()
    (tmp_path / "GEMINI.md").write_text("# Gemini\n", encoding="utf-8")
    _, load_line, _ = vp.parse_agent_config()
    updated = vp.sync_root_sot(tmp_path)
    assert updated == [tmp_path / "GEMINI.md"]
    assert load_line in (tmp_path / "GEMINI.md").read_text(encoding="utf-8")


def test_sync_agent_injection_sets_claude_config_version(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    summary = vp.default_rrr_status(0)
    vp.write_status_yaml(docs / vp.RRR_STATUS_NAME, summary)
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    issues = vp.sync_agent_injection(docs, tmp_path, force=True)
    assert error_codes(issues) == set()
    assert (docs / "agent.plan.md").is_file()
    reloaded, _ = vp.load_status(docs / vp.RRR_STATUS_NAME)
    assert reloaded is not None
    assert reloaded["claude_config_version"] == vp.parse_agent_config()[0]
    _, load_line, _ = vp.parse_agent_config()
    assert load_line in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "docs/agent.plan.md" in load_line


def test_independent_patches_ok(tmp_path: Path):
    write_planning(tmp_path)
    items = planning_items(tmp_path)
    write_planning(tmp_path, status=frozen_status(items, product="0.1.3", docs="0.1.7"))
    issues = vp.validate_dir(tmp_path)
    assert "HAND_BUMP" not in error_codes(issues)
    assert "CURRENT_NOT_PATCH" not in codes(issues)
    assert "NEXT_LOCKED" not in codes(issues)
    assert error_codes(issues) == set(), [i.format() for i in issues]


def test_lock_target_pin_refresh_ok(tmp_path: Path):
    write_planning(tmp_path)
    items = planning_items(tmp_path)
    status = frozen_status(items)
    es_digest = vp.compute_doc_digest(items, "executive-summary")
    status["levels"]["executive-summary"]["rev"] = 2
    status["levels"]["executive-summary"]["digest"] = es_digest
    status["levels"]["mrd"]["pins"]["executive-summary"] = {
        "rev": 2,
        "digest": es_digest,
    }
    status["docs"] = "0.1.8"
    status["mint_hash"] = vp.compute_mint_hash(status)
    write_planning(tmp_path, status=status)
    issues = vp.validate_dir(tmp_path)
    assert "STALE_PIN" not in error_codes(issues)
    assert error_codes(issues) == set(), [i.format() for i in issues]


def test_stale_pin_fails(tmp_path: Path):
    write_planning(tmp_path)
    items = planning_items(tmp_path)
    status = frozen_status(items)
    status["levels"]["mrd"]["pins"]["executive-summary"]["digest"] = "sha256:deadbeef"
    status["mint_hash"] = vp.compute_mint_hash(status)
    write_planning(tmp_path, status=status)
    issues = vp.validate_dir(tmp_path)
    assert "STALE_PIN" in error_codes(issues)


def test_parent_unfrozen_fails(tmp_path: Path):
    write_planning(tmp_path)
    items = planning_items(tmp_path)
    status = frozen_status(items, frozen=["mrd", "brd", "prd"])
    write_planning(tmp_path, status=status)
    issues = vp.validate_dir(tmp_path)
    assert "PARENT_UNFROZEN" in error_codes(issues)


def test_rev_while_open_fails(tmp_path: Path):
    write_planning(tmp_path)
    items = planning_items(tmp_path)
    status = frozen_status(items)
    write_planning(
        tmp_path,
        session={"frozen_levels": ["executive-summary", "mrd"]},
        status=status,
    )
    issues = vp.validate_dir(tmp_path)
    assert "REV_WHILE_OPEN" in error_codes(issues)


def test_rev_while_open_frontmatter(tmp_path: Path):
    files = {"executive-summary.md": """\
---
doc_type: executive-summary
track: "0.1"
doc_rev: 1
pins: {}
---

## ES-1: Competitive window
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must

> Why now.
"""}
    write_planning(tmp_path, files)
    items = planning_items(tmp_path)
    status = frozen_status(items, frozen=[])
    write_planning(tmp_path, files, status=status)
    issues = vp.validate_dir(tmp_path)
    assert "REV_WHILE_OPEN" in error_codes(issues)


def test_hand_bump_track(tmp_path: Path):
    write_planning(tmp_path)
    items = planning_items(tmp_path)
    status = frozen_status(items)
    status["track"] = "0.2"
    write_planning(tmp_path, status=status)
    issues = vp.validate_dir(tmp_path)
    assert "HAND_BUMP" in error_codes(issues)


def test_next_open_is_not_ci_fail(tmp_path: Path):
    write_planning(tmp_path)
    items = planning_items(tmp_path)
    write_planning(tmp_path, status=frozen_status(items, next_track="0.2"))
    issues = vp.validate_dir(tmp_path)
    assert "NEXT_LOCKED" not in codes(issues)
    assert "CURRENT_NOT_PATCH" not in codes(issues)
    assert error_codes(issues) == set(), [i.format() for i in issues]


def test_track_subdir_loads_parent_status(tmp_path: Path):
    write_planning(tmp_path)
    items = planning_items(tmp_path)
    status = frozen_status(items, next_track="0.2")
    write_planning(tmp_path, status=status)
    nxt = tmp_path / "0.2"
    nxt.mkdir()
    assert vp.find_status_path(nxt) == tmp_path / "status.yaml"
    assert vp.phase_root(nxt) == tmp_path
    issues = vp.check_baselines(nxt, [])
    assert "HAND_BUMP" not in error_codes(issues)
    assert error_codes(issues) == set(), [i.format() for i in issues]


def test_plan_pin_loads_discovery_status_across_dirs(tmp_path: Path) -> None:
    """Plan PRD pin check reads BRD rev/digest from docs/discovery/status.yaml."""
    docs = tmp_path / "docs"
    discovery = docs / "discovery"
    plan = docs / "plan"
    discovery_files = {
        name: VALID_FILES[name] for name in ("executive-summary.md", "mrd.md", "brd.md")
    }
    write_planning(discovery, discovery_files)
    disc_items = planning_items(discovery)
    disc_status = frozen_status(disc_items, frozen=["executive-summary", "mrd", "brd"])
    disc_status["levels"] = {
        k: v for k, v in disc_status["levels"].items() if k in vp.DISCOVERY_STEMS
    }
    disc_status["mint_hash"] = vp.compute_mint_hash(disc_status)
    write_planning(discovery, discovery_files, status=disc_status)

    write_planning(plan, {"prd.md": VALID_FILES["prd.md"]})
    plan_items = planning_items(plan)
    brd_digest = vp.compute_doc_digest(disc_items, "brd")
    plan_status = {
        "claude_config_version": 1,
        "track": "0.1",
        "product": "0.1.3",
        "docs": "0.1.7",
        "next": None,
        "docs_shipped": True,
        "product_status": "shipped",
        "levels": {
            "prd": {
                "rev": 1,
                "digest": vp.compute_doc_digest(plan_items, "prd"),
                "pins": {"brd": {"rev": 1, "digest": brd_digest}},
            }
        },
        "next_levels": {},
        "challenge": {},
        "next_challenge": {},
    }
    plan_status["mint_hash"] = vp.compute_mint_hash(plan_status)
    write_planning(
        plan,
        {"prd.md": VALID_FILES["prd.md"]},
        session={"frozen_levels": ["prd"]},
        status=plan_status,
    )
    issues = vp.check_baselines(plan, plan_items)
    assert "STALE_PIN" not in error_codes(issues)
    assert "PARENT_UNFROZEN" not in error_codes(issues)
    assert error_codes(issues) == set(), [i.format() for i in issues]

    plan_status["levels"]["prd"]["pins"]["brd"]["digest"] = "sha256:deadbeef"
    plan_status["mint_hash"] = vp.compute_mint_hash(plan_status)
    write_planning(plan, {"prd.md": VALID_FILES["prd.md"]}, status=plan_status)
    stale = vp.check_baselines(plan, plan_items)
    assert "STALE_PIN" in error_codes(stale)


def test_challenge_mutation_does_not_hand_bump(tmp_path: Path) -> None:
    write_planning(tmp_path)
    items = planning_items(tmp_path)
    status = frozen_status(items)
    recorded = status["mint_hash"]
    status["challenge"] = {
        "prd": {"status": "clean", "scanned_digest": status["levels"]["prd"]["digest"]}
    }
    assert status["mint_hash"] == recorded
    write_planning(tmp_path, status=status)
    issues = vp.check_baselines(tmp_path, items)
    assert "HAND_BUMP" not in error_codes(issues)
    assert error_codes(issues) == set(), [i.format() for i in issues]
