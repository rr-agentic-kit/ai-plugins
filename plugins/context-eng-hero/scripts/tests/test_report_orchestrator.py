"""Unit tests for audit_static.report and audit_static.orchestrator."""

from __future__ import annotations

from pathlib import Path

from audit_static.orchestrator import run_checks
from audit_static.report import check, format_markdown, severity_summary
from audit_static.runners import RUNNERS


def test_check_shape() -> None:
    # Arrange / Act
    passed = check("static.test.id", "major", True, "all good")
    failed = check("static.test.id", "critical", False, "broken")
    # Assert
    assert passed == {
        "id": "static.test.id",
        "severity": "major",
        "result": "PASS",
        "evidence": "all good",
    }
    assert failed["result"] == "FAIL"


def test_severity_summary_aggregation() -> None:
    # Arrange
    results = [
        check("a", "critical", True, "ok"),
        check("b", "critical", False, "bad"),
        check("c", "major", True, "ok"),
        check("d", "minor", True, "ok"),
        check("e", "minor", False, "warn"),
    ]
    # Act
    summary = severity_summary(results)
    # Assert
    assert summary == {
        "critical": {"pass": 1, "total": 2},
        "major": {"pass": 1, "total": 1},
        "minor": {"pass": 1, "total": 2},
    }


def test_format_markdown_includes_severity_summary() -> None:
    # Arrange
    results = [
        check("static.frontmatter.delimiters", "critical", True, "ok"),
        check("static.links.https-only", "critical", False, "http found"),
        check("static.naming.skill", "major", True, "ok"),
    ]
    # Act
    md = format_markdown(results, "skills/foo/SKILL.md", "skill")
    # Assert
    assert "# Static checks: skill — skills/foo/SKILL.md" in md
    assert "## Severity summary" in md
    assert "- Critical: 1/2" in md
    assert "- Major: 1/1" in md
    assert "- Minor: 0/0" in md
    assert "| static.frontmatter.delimiters | critical | PASS | ok |" in md
    assert "| static.links.https-only | critical | FAIL | http found |" in md


def test_format_markdown_single_severity_summary_binding() -> None:
    # Arrange — CP032: header counts must come from severity_summary once
    results = [
        check("only.major", "major", False, "x"),
        check("only.major2", "major", True, "y"),
    ]
    # Act
    md = format_markdown(results, "path.md", "workflow")
    # Assert
    assert md.count("## Severity summary") == 1
    assert "- Major: 1/2" in md
    assert "- Critical: 0/0" in md


def test_run_checks_early_return_on_load_failure(tmp_path: Path) -> None:
    # Arrange
    plugin_root = tmp_path / "plugin"
    plugin_root.mkdir()
    # Act
    results = run_checks(plugin_root, "nonexistent/SKILL.md")
    # Assert
    assert len(results) == 1
    assert results[0]["id"] == "static.file.exists"
    assert results[0]["result"] == "FAIL"


def test_run_checks_runs_ordered_runners(tmp_path: Path) -> None:
    # Arrange
    plugin_root = tmp_path / "plugin"
    rel_path = "skills/my-skill/SKILL.md"
    skill_path = plugin_root / rel_path
    skill_path.parent.mkdir(parents=True)
    skill_path.write_text(
        """---
name: my-skill
description: A valid test skill for orchestrator coverage.
---

# My Skill

## When to use

- testing

## Load order

1. step
""",
        encoding="utf-8",
    )
    # Act
    results = run_checks(plugin_root, rel_path)
    # Assert
    ids = [r["id"] for r in results]
    first_frontmatter = next(
        i for i, rid in enumerate(ids) if rid.startswith("static.frontmatter")
    )
    first_links = next(i for i, rid in enumerate(ids) if rid.startswith("static.links"))
    assert first_frontmatter < first_links
    assert len(results) > len(RUNNERS)
