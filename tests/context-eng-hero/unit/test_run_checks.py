"""Unit tests for run_checks against fixture mini-plugins."""

from __future__ import annotations

from pathlib import Path

import audit_static as m
import pytest
from conftest import all_pass, result_by_id


@pytest.mark.parametrize(
    ("case", "rel_path", "expect_pass"),
    [
        ("skill_valid", "skills/my-skill/SKILL.md", True),
        ("skill_bad_name", "skills/my-skill/SKILL.md", False),
        ("skill_missing_sections", "skills/my-skill/SKILL.md", False),
        ("skill_bad_yaml", "skills/my-skill/SKILL.md", False),
        ("skill_no_opening_delim", "skills/my-skill/SKILL.md", False),
        ("skill_parent_path", "skills/my-skill/SKILL.md", False),
        ("skill_broken_link", "skills/my-skill/SKILL.md", False),
        ("skill_valid_link", "skills/my-skill/SKILL.md", True),
        ("skill_http_link", "skills/my-skill/SKILL.md", False),
        ("skill_long_description", "skills/my-skill/SKILL.md", False),
        ("command_valid", "commands/my-cmd.md", True),
        ("command_missing_output", "commands/my-cmd.md", False),
        ("workflow_valid", "docs/my-workflow.md", True),
        ("workflow_no_fm", "docs/plain-workflow.md", True),
        ("ref_file_no_fm", "skills/my-skill/refs/foo.md", True),
        (
            "ref_file_no_fm",
            "skills/my-skill/refs/doc-standards/es.md",
            True,
        ),
        ("agent_valid", "agents/my-agent.md", True),
        ("rule_valid", "rules/my-rule.mdc", True),
    ],
)
def test_fixture_trees(mini_plugin, case: str, rel_path: str, expect_pass: bool):
    root = mini_plugin(case)
    results = m.run_checks(root, rel_path)
    assert all_pass(results) == expect_pass


def test_missing_file(mini_plugin):
    root = mini_plugin("skill_valid")
    results = m.run_checks(root, "missing.md")
    row = result_by_id(results, "static.file.exists")
    assert row["result"] == "FAIL"


def test_path_outside_plugin(mini_plugin, tmp_path):
    root = mini_plugin("skill_valid")
    outside = tmp_path / "escape.md"
    outside.write_text("x", encoding="utf-8")
    results = m.run_checks(root, str(outside))
    assert any(
        r["id"] == "static.paths.within-plugin" and r["result"] == "FAIL"
        for r in results
    )


@pytest.mark.parametrize(
    ("case", "rel_path", "check_id"),
    [
        ("skill_bad_name", "skills/my-skill/SKILL.md", "static.name.path-match"),
        (
            "skill_missing_sections",
            "skills/my-skill/SKILL.md",
            "static.sections.required",
        ),
        (
            "skill_bad_yaml",
            "skills/my-skill/SKILL.md",
            "static.frontmatter.parseable",
        ),
        (
            "skill_parent_path",
            "skills/my-skill/SKILL.md",
            "static.paths.no-parent-segment",
        ),
        (
            "skill_broken_link",
            "skills/my-skill/SKILL.md",
            "static.links.internal-resolve",
        ),
        (
            "skill_http_link",
            "skills/my-skill/SKILL.md",
            "static.links.https-only",
        ),
        (
            "skill_long_description",
            "skills/my-skill/SKILL.md",
            "static.description.max-length",
        ),
        ("command_missing_output", "commands/my-cmd.md", "static.sections.required"),
    ],
)
def test_specific_check_fails(mini_plugin, case: str, rel_path: str, check_id: str):
    root = mini_plugin(case)
    results = m.run_checks(root, rel_path)
    assert result_by_id(results, check_id)["result"] == "FAIL"


def test_workflow_optional_frontmatter_passes(mini_plugin):
    root = mini_plugin("workflow_no_fm")
    results = m.run_checks(root, "docs/plain-workflow.md")
    delim = result_by_id(results, "static.frontmatter.delimiters")
    assert delim["result"] == "PASS"
    assert "optional" in delim["evidence"]


def test_ref_file_optional_frontmatter_passes(mini_plugin):
    root = mini_plugin("ref_file_no_fm")
    results = m.run_checks(root, "skills/my-skill/refs/foo.md")
    assert all_pass(results)
    delim = result_by_id(results, "static.frontmatter.delimiters")
    assert delim["result"] == "PASS"
    assert "optional" in delim["evidence"]
    assert not any(r["id"] == "static.description.present" for r in results)
    assert not any(r["id"] == "static.sections.required" for r in results)


def test_nested_ref_file_no_sections_required(mini_plugin):
    root = mini_plugin("ref_file_no_fm")
    rel = "skills/my-skill/refs/doc-standards/es.md"
    assert m.detect_type(Path(rel)) == "ref-file"
    results = m.run_checks(root, rel)
    assert all_pass(results)
    assert not any(r["id"] == "static.sections.required" for r in results)
    ids = [r["id"] for r in results]
    assert len(ids) == len(set(ids)), "duplicate check ids"
