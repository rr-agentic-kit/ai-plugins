"""Unit tests for run_checks against fixture mini-plugins."""

from __future__ import annotations

from pathlib import Path

import audit_static as m
import pytest
from audit_static import models as models_mod
from audit_static.models import AuditContext

from conftest import FIXTURE_CASES, all_pass, result_by_id


@pytest.mark.parametrize(
    ("case", "rel_path", "expect_pass"),
    FIXTURE_CASES,
    ids=[f"{c}-{p}" for c, p, _ in FIXTURE_CASES],
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


def test_models_load_size_cap(mini_plugin, monkeypatch):
    root = mini_plugin("skill_valid")
    monkeypatch.setattr(models_mod, "MAX_READ_BYTES", 10)
    loaded = AuditContext.load(root, "skills/my-skill/SKILL.md")
    assert isinstance(loaded, list)
    row = result_by_id(loaded, "static.file.size")
    assert row["result"] == "FAIL"
    assert "exceeds size cap" in row["evidence"]
    # Early bail: only the size check, no runner rows.
    assert [r["id"] for r in loaded] == ["static.file.size"]


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
            "skill_absolute_path",
            "skills/my-skill/SKILL.md",
            "static.paths.no-absolute",
        ),
        (
            "skill_bad_name_format",
            "skills/my-skill/SKILL.md",
            "static.name.format",
        ),
        (
            "skill_missing_description",
            "skills/my-skill/SKILL.md",
            "static.keys.required",
        ),
        (
            "skill_missing_description",
            "skills/my-skill/SKILL.md",
            "static.description.present",
        ),
        (
            "skill_medium_description",
            "skills/my-skill/SKILL.md",
            "static.description.recommended-length",
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
        (
            "workflow_missing_todo",
            "docs/my-workflow.md",
            "static.workflow.todo-id",
        ),
        (
            "workflow_duplicate_todo",
            "docs/my-workflow.md",
            "static.workflow.todo-id",
        ),
    ],
)
def test_specific_check_fails(mini_plugin, case: str, rel_path: str, check_id: str):
    root = mini_plugin(case)
    results = m.run_checks(root, rel_path)
    assert result_by_id(results, check_id)["result"] == "FAIL"


def test_workflow_todo_fail_evidence(mini_plugin):
    missing = m.run_checks(mini_plugin("workflow_missing_todo"), "docs/my-workflow.md")
    assert "no todo_id" in result_by_id(missing, "static.workflow.todo-id")["evidence"]
    dup = m.run_checks(mini_plugin("workflow_duplicate_todo"), "docs/my-workflow.md")
    assert "duplicate" in result_by_id(dup, "static.workflow.todo-id")["evidence"]


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
