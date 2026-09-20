"""Unit tests for detect_type."""

from __future__ import annotations

from pathlib import Path

import audit_static as m
import pytest


@pytest.mark.parametrize(
    ("rel", "expected"),
    [
        ("skills/recipe-context-engineer/SKILL.md", "skill"),
        ("skills/x/README.md", "skill-readme"),
        ("skills/x/refs/foo.md", "ref-file"),
        ("skills/x/refs/doc-standards/es.md", "ref-file"),
        ("skills/x/references/foo.md", "ref-file"),
        ("commands/context-engineer-audit.md", "command"),
        ("agents/foo.md", "agent"),
        ("rules/x.mdc", "rule"),
        (".cursor/rules/x.mdc", "rule"),
        ("docs/release-workflow.md", "workflow"),
        ("docs/notes.md", "workflow"),
        ("ACRONYMS.md", "acronyms"),
        ("GLOSSARY.md", "glossary"),
    ],
)
def test_detect_type(rel: str, expected: str):
    assert m.detect_type(Path(rel)) == expected
