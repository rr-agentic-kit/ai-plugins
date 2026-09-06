"""Layout migrate: phase-first, track subdirs, legacy docs/plans/."""

from __future__ import annotations

from pathlib import Path

import validate_planning_script as vp
from validate_planning_script.layout_migrate import migrate_docs_layout


def test_migrate_already_ok(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    rr = docs / "rr"
    rr.mkdir(parents=True)
    (rr / "rrr-status.yaml").write_text(
        "track: '0.1'\nphase: discovery\n", encoding="utf-8"
    )
    status, message = migrate_docs_layout(docs)
    assert status == "ok"
    assert "migrated" in message


def test_migrate_phase_first(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    discovery = docs / "discovery"
    plan = docs / "plan"
    discovery.mkdir(parents=True)
    plan.mkdir(parents=True)
    (discovery / "brd.md").write_text("# BRD\n", encoding="utf-8")
    (plan / "prd.md").write_text("# PRD\n", encoding="utf-8")
    (docs / "rrr-status.yaml").write_text(
        "track: '0.1'\nphase: discovery\nsummary: x\n", encoding="utf-8"
    )
    (docs / "future.md").write_text("# Future\n", encoding="utf-8")
    status, message = migrate_docs_layout(docs)
    assert status == "fixed"
    assert "moved" in message
    rr = docs / "rr"
    assert (rr / "0.1" / "discovery" / "brd.md").is_file()
    assert (rr / "0.1" / "plan" / "prd.md").is_file()
    assert (rr / "rrr-status.yaml").is_file()
    assert (rr / "future.md").is_file()
    assert not discovery.exists()
    assert not plan.exists()
    assert not (docs / "rrr-status.yaml").exists()
    second, msg2 = migrate_docs_layout(docs)
    assert second == "ok"
    assert "migrated" in msg2


def test_migrate_phase_first_track_subdirs(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    discovery = docs / "discovery"
    nxt = discovery / "0.2"
    nxt.mkdir(parents=True)
    (nxt / "executive-summary.md").write_text("# ES next\n", encoding="utf-8")
    (discovery / "brd.md").write_text("# BRD\n", encoding="utf-8")
    (docs / "rrr-status.yaml").write_text(
        "track: '0.1'\nnext: '0.2'\n", encoding="utf-8"
    )
    status, _ = migrate_docs_layout(docs)
    assert status == "fixed"
    assert (docs / "rr" / "0.2" / "discovery" / "executive-summary.md").is_file()
    assert (docs / "rr" / "0.1" / "discovery" / "brd.md").is_file()
    assert not (docs / "discovery").exists()


def test_migrate_legacy_plans(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    plans = docs / "plans"
    plans.mkdir(parents=True)
    (plans / "executive-summary.md").write_text("# ES\n", encoding="utf-8")
    (plans / "prd.md").write_text("# PRD\n", encoding="utf-8")
    (plans / "architecture.md").write_text("# Arch\n", encoding="utf-8")
    (plans / "deltas").mkdir()
    (plans / "deltas" / "PRD-1.md").write_text("# Delta\n", encoding="utf-8")
    (plans / "status.yaml").write_text("track: '0.1'\nlevels: {}\n", encoding="utf-8")
    status, _ = migrate_docs_layout(docs)
    assert status == "fixed"
    disc = docs / "rr" / "0.1" / "discovery"
    plan = docs / "rr" / "0.1" / "plan"
    assert (disc / "executive-summary.md").is_file()
    assert (plan / "prd.md").is_file()
    assert (plan / "architecture.md").is_file()
    assert (plan / "deltas" / "PRD-1.md").is_file()
    assert (disc / "status.yaml").is_file()
    assert not plans.exists()


def test_find_rrr_status_prefers_rr(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    legacy = docs / "rrr-status.yaml"
    legacy.write_text("track: '0.1'\n", encoding="utf-8")
    assert vp.find_rrr_status_path(docs) == legacy
    rr = docs / "rr"
    rr.mkdir()
    modern = rr / "rrr-status.yaml"
    modern.write_text("track: '0.2'\n", encoding="utf-8")
    assert vp.find_rrr_status_path(docs) == modern
    assert vp.current_track(docs) == "0.2"


def test_track_phase_helpers(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    assert vp.rr_root(docs) == docs / "rr"
    assert vp.tasks_dir(docs) == docs / "rr" / "tasks"
    assert vp.rrr_status_path(docs) == docs / "rr" / "rrr-status.yaml"
    assert (
        vp.track_phase_dir(docs, "0.1", "discovery")
        == docs / "rr" / "0.1" / "discovery"
    )
