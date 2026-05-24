"""Unit tests for detect_type."""

from __future__ import annotations

from pathlib import Path

import audit_static as m


def test_skill_path():
    rel = Path("skills/context-engineer/SKILL.md")
    assert m.detect_type(rel) == "skill"


def test_command_path():
    rel = Path("commands/context-engineer-audit.md")
    assert m.detect_type(rel) == "command"


def test_agent_path():
    rel = Path("agents/foo.md")
    assert m.detect_type(rel) == "agent"


def test_rule_mdc():
    assert m.detect_type(Path("rules/x.mdc")) == "rule"


def test_rule_cursor_dir():
    assert m.detect_type(Path(".cursor/rules/x.mdc")) == "rule"


def test_workflow_by_stem():
    assert m.detect_type(Path("docs/release-workflow.md")) == "workflow"


def test_default_workflow():
    assert m.detect_type(Path("docs/notes.md")) == "workflow"
