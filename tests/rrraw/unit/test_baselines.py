"""Cascade baselines: status.yaml, agent.plan.md, pins, mechanical CI codes."""

from __future__ import annotations

from pathlib import Path

import validate_planning as vp
from helpers import (
    codes,
    error_codes,
    frozen_status,
    planning_items,
    write_planning,
)

BOGUS_ES = """\
## ES-99: Bogus inbox item
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must
"""


def test_parse_agent_config_from_refs():
    version, load_line, body = vp.parse_agent_config()
    assert version == 1
    assert "agent.plan.md" in load_line
    assert "Do not remove this line" in load_line
    template = vp.AGENT_PLAN_TEMPLATE_PATH.read_text(encoding="utf-8")
    assert body == template
    assert "<!-- agent-plan-template -->" not in body
    config = vp.AGENT_CONFIG_PATH.read_text(encoding="utf-8")
    assert "<!-- agent-plan-template -->" not in config
    assert "status.yaml" in body
    assert "rr-planner" in body
    assert "Do not delete this file" in body
    assert "## Pairing" not in body


def test_emit_agent_plan(tmp_path: Path):
    path = vp.emit_agent_plan(tmp_path)
    assert path == tmp_path / "agent.plan.md"
    text = path.read_text(encoding="utf-8")
    assert text.startswith("# Planning pairing")
    assert "status.yaml" in text
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
    plans = tmp_path / "docs" / "plans"
    write_planning(plans)
    items = planning_items(plans)
    status = frozen_status(items, claude_config_version=0)
    write_planning(plans, status=status)
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    issues = vp.sync_agent_injection(plans, tmp_path, force=True)
    assert error_codes(issues) == set()
    assert (plans / "agent.plan.md").is_file()
    reloaded, _ = vp.load_status(plans / "status.yaml")
    assert reloaded is not None
    assert reloaded["claude_config_version"] == vp.parse_agent_config()[0]
    assert reloaded["mint_hash"] == vp.compute_mint_hash(reloaded)
    _, load_line, _ = vp.parse_agent_config()
    assert load_line in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")


def test_sync_cli_greenfield(tmp_path: Path):
    plans = tmp_path / "docs" / "plans"
    plans.mkdir(parents=True)
    (tmp_path / "CLAUDE.md").write_text("# Project\n", encoding="utf-8")
    assert (
        vp.main(
            [
                str(plans),
                "--sync-agent-config",
                "--repo-root",
                str(tmp_path),
            ]
        )
        == 0
    )
    assert (plans / "agent.plan.md").is_file()
    _, load_line, _ = vp.parse_agent_config()
    assert load_line in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")


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
    es_digest = vp.compute_doc_digest(items, "exec-summary")
    status["levels"]["exec-summary"]["rev"] = 2
    status["levels"]["exec-summary"]["digest"] = es_digest
    status["levels"]["mrd"]["pins"]["exec-summary"] = {
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
    status["levels"]["mrd"]["pins"]["exec-summary"]["digest"] = "sha256:deadbeef"
    status["mint_hash"] = vp.compute_mint_hash(status)
    write_planning(tmp_path, status=status)
    issues = vp.validate_dir(tmp_path)
    assert "STALE_PIN" in error_codes(issues)


def test_parent_unfrozen_fails(tmp_path: Path):
    write_planning(tmp_path)
    items = planning_items(tmp_path)
    status = frozen_status(items, frozen=["mrd", "brd", "prd", "frd"])
    write_planning(tmp_path, status=status)
    issues = vp.validate_dir(tmp_path)
    assert "PARENT_UNFROZEN" in error_codes(issues)


def test_rev_while_open_fails(tmp_path: Path):
    write_planning(tmp_path)
    items = planning_items(tmp_path)
    status = frozen_status(items)
    write_planning(
        tmp_path,
        session={"frozen_levels": ["exec-summary", "mrd"]},
        status=status,
    )
    issues = vp.validate_dir(tmp_path)
    assert "REV_WHILE_OPEN" in error_codes(issues)


def test_rev_while_open_frontmatter(tmp_path: Path):
    files = {
        "exec-summary.md": """\
---
doc_type: exec-summary
track: "0.1"
doc_rev: 1
pins: {}
---

## ES-1: Competitive window
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must

> Why now.
"""
    }
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


def test_future_md_ignored(tmp_path: Path):
    write_planning(tmp_path)
    (tmp_path / vp.FUTURE_NAME).write_text(BOGUS_ES, encoding="utf-8")
    (tmp_path / vp.AGENT_PLAN_NAME).write_text(BOGUS_ES, encoding="utf-8")
    issues = vp.validate_dir(tmp_path)
    assert error_codes(issues) == set(), [i.format() for i in issues]
    assert not any(issue.item_id == "ES-99" for issue in issues)


def test_missing_status_yaml_skips_baseline_codes(tmp_path: Path):
    write_planning(tmp_path)
    issues = vp.validate_dir(tmp_path)
    assert error_codes(issues) == set(), [i.format() for i in issues]
    assert "HAND_BUMP" not in codes(issues)
    assert "STALE_PIN" not in codes(issues)


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
    issues = vp.check_baselines(nxt, [])
    assert "HAND_BUMP" not in error_codes(issues)
    assert error_codes(issues) == set(), [i.format() for i in issues]
