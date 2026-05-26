"""Regression: real context-eng-hero plugin artifacts pass static audit."""

from __future__ import annotations

from pathlib import Path

import audit_static as m
import pytest
from conftest import PLUGIN_ROOT, all_pass


def test_recipe_context_engineer_skill(plugin_root):
    results = m.run_checks(plugin_root, "skills/recipe-context-engineer/SKILL.md")
    assert all_pass(results), [r for r in results if r["result"] == "FAIL"]


def test_recipe_static_memory_skill(plugin_root):
    results = m.run_checks(plugin_root, "skills/recipe-static-memory/SKILL.md")
    assert all_pass(results), [r for r in results if r["result"] == "FAIL"]


@pytest.mark.parametrize(
    "command_file",
    sorted((PLUGIN_ROOT / "commands").glob("context-engineer-*.md"))
    + sorted((PLUGIN_ROOT / "commands").glob("static-memory-*.md")),
)
def test_action_commands_pass(command_file: Path, plugin_root):
    rel = command_file.relative_to(plugin_root).as_posix()
    results = m.run_checks(plugin_root, rel)
    assert all_pass(results), f"{rel}: {[r for r in results if r['result'] == 'FAIL']}"
