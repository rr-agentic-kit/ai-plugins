"""Regression: real context-eng-hero plugin artifacts pass static audit."""

from __future__ import annotations

from pathlib import Path

import pytest

import audit_static as m
from conftest import PLUGIN_ROOT, all_pass


def test_context_engineer_skill(plugin_root):
    results = m.run_checks(plugin_root, "skills/context-engineer/SKILL.md")
    assert all_pass(results), [r for r in results if r["result"] == "FAIL"]


@pytest.mark.parametrize(
    "command_file",
    sorted((PLUGIN_ROOT / "commands").glob("context-engineer-*.md")),
)
def test_action_commands_pass(command_file: Path, plugin_root):
    rel = command_file.relative_to(plugin_root).as_posix()
    results = m.run_checks(plugin_root, rel)
    assert all_pass(results), f"{rel}: {[r for r in results if r['result'] == 'FAIL']}"
