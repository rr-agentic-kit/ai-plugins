"""Unit tests for audit_static detect, frontmatter, and headings modules."""

from __future__ import annotations

from pathlib import Path

import audit_static
import pytest
from audit_static.detect import detect_type
from audit_static.frontmatter import parse_frontmatter
from audit_static.headings import headings_present


@pytest.mark.parametrize(
    ("rel_path", "expected"),
    [
        (Path("skills/recipe-context-engineer/SKILL.md"), "skill"),
        (Path("skills/recipe-context-engineer/README.md"), "skill-readme"),
        (Path("commands/audit.md"), "command"),
        (Path("agents/reviewer.md"), "agent"),
        (Path("rules/style.mdc"), "rule"),
        (Path(".cursor/rules/lint.mdc"), "rule"),
        (Path("workflows/deploy-workflow.md"), "workflow"),
        (Path("skills/recipe-context-engineer/refs/actions/audit.md"), "unknown"),
        (Path("README.md"), "unknown"),
        (Path("docs/notes.md"), "workflow"),
    ],
)
def test_detect_type(rel_path: Path, expected: str) -> None:
    # Arrange — rel_path is the plugin-relative artifact path under test
    # Act
    result = detect_type(rel_path)
    # Assert
    assert result == expected


@pytest.mark.parametrize(
    ("text", "expected_data", "expected_error"),
    [
        (
            "---\nname: test\ndescription: ok\n---\n\n# Body\n",
            {"name": "test", "description": "ok"},
            None,
        ),
        (
            "# No frontmatter\n",
            None,
            "missing opening --- delimiter",
        ),
        (
            "---\nname: test\n",
            None,
            "missing closing --- delimiter",
        ),
    ],
)
def test_parse_frontmatter_valid_and_missing_delimiters(
    text: str,
    expected_data: dict | None,
    expected_error: str | None,
) -> None:
    # Arrange — text is the full markdown document
    # Act
    data, body, error = parse_frontmatter(text)
    # Assert
    assert data == expected_data
    assert error == expected_error
    if expected_data is not None:
        assert body.startswith("# Body")


def test_parse_frontmatter_without_pyyaml(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setattr(audit_static, "yaml", None)
    text = "---\nname: test\n---\n\n# Body\n"
    # Act
    data, body, error = parse_frontmatter(text)
    # Assert
    assert data is None
    assert body == "# Body\n"
    assert error is not None
    assert "pyyaml not installed" in error


def test_headings_present_extracts_level_two_headings() -> None:
    # Arrange
    body = "# Title\n\n## When to use\n\nText.\n\n## Load order\n\n1. step\n"
    # Act
    found = headings_present(body)
    # Assert
    assert found == {"When to use", "Load order"}
