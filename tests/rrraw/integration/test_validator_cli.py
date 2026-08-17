"""CLI flags and exit codes (in-process)."""

from __future__ import annotations

from pathlib import Path

import validate_planning_script as vp
from helpers import write_planning


def test_cli_ok(tmp_path: Path):
    write_planning(tmp_path)
    assert vp.main([str(tmp_path)]) == 0


def test_cli_fail(tmp_path: Path):
    write_planning(tmp_path, write_json=False)
    assert vp.main([str(tmp_path)]) == 1


def test_cli_missing_dir(tmp_path: Path):
    assert vp.main([str(tmp_path / "nope")]) == 1


def test_cli_json_format_errors(tmp_path: Path):
    write_planning(tmp_path)
    assert vp.main([str(tmp_path), "--format", "json"]) == 1


def test_cli_yaml_format_errors(tmp_path: Path):
    write_planning(tmp_path)
    assert vp.main([str(tmp_path), "--format", "yaml"]) == 1


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
