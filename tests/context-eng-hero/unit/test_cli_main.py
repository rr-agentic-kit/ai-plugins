"""Direct unit tests for audit_static.cli (coverage for main() and path resolution)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from audit_static.cli import _resolve_relative_path, main
from conftest import _ensure_lexicon_companions

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


def _write_skill(plugin_root: Path, folder: str, body: str) -> None:
    skill_dir = plugin_root / "skills" / folder
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")


def test_resolve_relative_path_single_skill(tmp_path: Path) -> None:
    _write_skill(tmp_path, "lone-skill", _VALID_SKILL)
    assert _resolve_relative_path(tmp_path, ".") == "skills/lone-skill/SKILL.md"


def test_resolve_relative_path_explicit_path(tmp_path: Path) -> None:
    _write_skill(tmp_path, "lone-skill", _VALID_SKILL)
    assert (
        _resolve_relative_path(tmp_path, "skills/lone-skill/SKILL.md")
        == "skills/lone-skill/SKILL.md"
    )


def test_resolve_relative_path_ambiguous_skills_exits_with_paths(
    tmp_path: Path,
) -> None:
    _write_skill(
        tmp_path, "alpha-skill", _VALID_SKILL.replace("lone-skill", "alpha-skill")
    )
    _write_skill(
        tmp_path, "beta-skill", _VALID_SKILL.replace("lone-skill", "beta-skill")
    )
    with pytest.raises(SystemExit) as exc_info:
        _resolve_relative_path(tmp_path, ".")
    message = str(exc_info.value)
    assert "ambiguous" in message
    assert "skills/alpha-skill/SKILL.md" in message
    assert "skills/beta-skill/SKILL.md" in message


def test_resolve_relative_path_no_skills_exits(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exc_info:
        _resolve_relative_path(tmp_path, ".")
    assert "no skills/*/SKILL.md" in str(exc_info.value)


def test_main_markdown_exit_zero_when_all_checks_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    rel = "skills/lone-skill/SKILL.md"
    _write_skill(tmp_path, "lone-skill", _VALID_SKILL)
    _ensure_lexicon_companions(tmp_path)
    monkeypatch.setattr(sys, "argv", ["audit_static", str(tmp_path), rel])
    code = main()
    captured = capsys.readouterr()
    assert code == 0
    assert "## Static checks" in captured.out
    assert "Severity summary" in captured.out


def test_main_json_format(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    rel = "skills/lone-skill/SKILL.md"
    _write_skill(tmp_path, "lone-skill", _VALID_SKILL)
    _ensure_lexicon_companions(tmp_path)
    monkeypatch.setattr(
        sys, "argv", ["audit_static", str(tmp_path), rel, "--format", "json"]
    )
    code = main()
    captured = capsys.readouterr()
    assert code == 0
    data = json.loads(captured.out)
    assert isinstance(data, list)
    for row in data:
        assert set(row.keys()) >= {"id", "severity", "result", "evidence"}


def test_main_exit_one_when_any_check_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    rel = "skills/broken-skill/SKILL.md"
    skill_dir = tmp_path / "skills" / "broken-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(_INVALID_SKILL, encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["audit_static", str(tmp_path), rel])
    code = main()
    captured = capsys.readouterr()
    assert code == 1
    assert "FAIL" in captured.out


def test_main_ambiguous_dot_path_exits_nonzero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_skill(
        tmp_path, "alpha-skill", _VALID_SKILL.replace("lone-skill", "alpha-skill")
    )
    _write_skill(
        tmp_path, "beta-skill", _VALID_SKILL.replace("lone-skill", "beta-skill")
    )
    monkeypatch.setattr(sys, "argv", ["audit_static", str(tmp_path), "."])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert "ambiguous" in str(exc_info.value)
