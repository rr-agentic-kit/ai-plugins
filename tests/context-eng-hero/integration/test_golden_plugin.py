"""Regression: real context-eng-hero plugin artifacts pass static audit."""

from __future__ import annotations

import audit_static as m
from conftest import all_pass


def test_recipe_context_engineer_skill(plugin_root):
    results = m.run_checks(plugin_root, "skills/recipe-context-engineer/SKILL.md")
    assert all_pass(results), [r for r in results if r["result"] == "FAIL"]


def test_recipe_static_memory_skill(plugin_root):
    results = m.run_checks(plugin_root, "skills/recipe-static-memory/SKILL.md")
    assert all_pass(results), [r for r in results if r["result"] == "FAIL"]
