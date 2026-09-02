"""CLI tests for audit_static entrypoint and path resolution."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from audit_static.cli import _resolve_relative_path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
AUDIT_CLI = SCRIPTS_DIR / "audit_static.py"

_VALID_SKILL = """\
---
name: lone-skill
description: A minimal valid skill for CLI smoke tests.
---

# Lone skill

## Purpose

Exercise audit_static CLI exit codes.

## When to use

During unit tests.

## Procedure

1. Run the CLI.
"""

_INVALID_SKILL = """\
# Missing frontmatter

## Purpose

Should fail static checks.
"""


def _write_skill(plugin_root: Path, folder: str, body: str) -> Path:
    skill_dir = plugin_root / "skills" / folder
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(body, encoding="utf-8")
    return skill_path


def _run_audit(
    plugin_root: Path, relative_path: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AUDIT_CLI), str(plugin_root), relative_path],
        capture_output=True,
        text=True,
        check=False,
    )


def test_resolve_relative_path_single_skill(tmp_path: Path) -> None:
    # Arrange
    _write_skill(tmp_path, "lone-skill", _VALID_SKILL)
    # Act
    resolved = _resolve_relative_path(tmp_path, ".")
    # Assert
    assert resolved == "skills/lone-skill/SKILL.md"


def test_resolve_relative_path_explicit_path(tmp_path: Path) -> None:
    # Arrange
    _write_skill(tmp_path, "lone-skill", _VALID_SKILL)
    # Act
    resolved = _resolve_relative_path(tmp_path, "skills/lone-skill/SKILL.md")
    # Assert
    assert resolved == "skills/lone-skill/SKILL.md"


def test_resolve_relative_path_ambiguous_skills_exits_with_paths(
    tmp_path: Path,
) -> None:
    # Arrange
    _write_skill(
        tmp_path, "alpha-skill", _VALID_SKILL.replace("lone-skill", "alpha-skill")
    )
    _write_skill(
        tmp_path, "beta-skill", _VALID_SKILL.replace("lone-skill", "beta-skill")
    )
    # Act / Assert
    with pytest.raises(SystemExit) as exc_info:
        _resolve_relative_path(tmp_path, ".")
    message = str(exc_info.value)
    assert "ambiguous" in message
    assert "skills/alpha-skill/SKILL.md" in message
    assert "skills/beta-skill/SKILL.md" in message


def test_resolve_relative_path_no_skills_exits(tmp_path: Path) -> None:
    # Arrange — empty plugin tree
    # Act / Assert
    with pytest.raises(SystemExit) as exc_info:
        _resolve_relative_path(tmp_path, ".")
    assert "no skills/*/SKILL.md" in str(exc_info.value)


def test_main_subprocess_exit_zero_when_all_checks_pass(tmp_path: Path) -> None:
    # Arrange
    rel = "skills/lone-skill/SKILL.md"
    _write_skill(tmp_path, "lone-skill", _VALID_SKILL)
    # Act
    result = _run_audit(tmp_path, rel)
    # Assert
    assert result.returncode == 0, result.stdout + result.stderr


def test_main_subprocess_exit_one_when_any_check_fails(tmp_path: Path) -> None:
    # Arrange
    rel = "skills/broken-skill/SKILL.md"
    skill_dir = tmp_path / "skills" / "broken-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(_INVALID_SKILL, encoding="utf-8")
    # Act
    result = _run_audit(tmp_path, rel)
    # Assert
    assert result.returncode == 1, result.stdout + result.stderr
    assert "FAIL" in result.stdout


def test_main_subprocess_ambiguous_dot_path_exits_nonzero(tmp_path: Path) -> None:
    # Arrange
    _write_skill(
        tmp_path, "alpha-skill", _VALID_SKILL.replace("lone-skill", "alpha-skill")
    )
    _write_skill(
        tmp_path, "beta-skill", _VALID_SKILL.replace("lone-skill", "beta-skill")
    )
    # Act
    result = _run_audit(tmp_path, ".")
    # Assert
    assert result.returncode != 0
    assert "ambiguous" in result.stderr
