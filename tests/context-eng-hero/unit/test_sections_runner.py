"""Unit tests for audit_static.runners.sections."""

from __future__ import annotations

from pathlib import Path

import pytest
from audit_static.models import AuditContext
from audit_static.runners.sections import run_sections

_VALID_SKILL = """\
---
name: test-skill
description: Short valid skill description.
---

# Test skill

## Purpose

Purpose text.

## When to use

When testing.

## Procedure

1. Step one.
"""

_VALID_COMMAND = """\
---
name: test-cmd
description: Short command description.
---

# Test command

## Input contract

Inputs here.

## Execution

Run steps.

## Output

Expected output.
"""

_VALID_AGENT = """\
---
name: test-agent
description: Short agent description.
---

# Test agent

## Role

Role text.

## Tools and boundaries

Boundaries.

## Stop conditions

Stop rules.

## Outputs

Outputs.
"""

_VALID_RULE = """\
---
description: Rule description text.
---

# Test rule

## Intent

Intent text.

## Requirements

Requirements.

## Scope

Scope.

## Exceptions

Exceptions.
"""

_VALID_WORKFLOW = """\
# Test workflow

## Outcome

Outcome text.

## Steps

Steps.

## Delegation

Delegation.

## Exit and failure

Failure handling.

## Orchestration

Orchestration notes.
"""

_VALID_SKILL_README = """\
# Test skill

One-line outcome sentence.

## Why

Problem and audience.

## What

Capabilities and boundaries.

## When

### Use when

- Use when testing README static checks.

### Avoid when

- Do not use for production code review.

## Constraints

Self-invoke; static + reflection + pre-ship before write.

Source of truth: `SKILL.md`. This README is the human spec—not a Procedure echo.
"""

_ORCHESTRATOR_SKILL = """\
---
name: test-skill
description: Orchestrator skill for section tests.
---

# Test skill

## Purpose

Purpose text.

## When to use

When testing.

## Procedure

1. Step one.

## Actions

| Action id | Outcome | Run |
|-----------|---------|-----|
| create | New artifact | refs/actions/create.md |
| extract | Draft from context | refs/actions/extract.md |
| audit | Static + rubric report | refs/actions/audit.md |
| fix | Minimal edits | refs/actions/fix.md |
"""

_ORCHESTRATOR_README_WITH_ACTIONS = """\
# Test skill

One-line outcome sentence.

## Why

Problem and audience.

## What

Capabilities and boundaries.

## Actions

| Action | Outcome | Pick when |
|--------|---------|-----------|
| create | New artifact | User wants a new file |
| extract | Draft from context | SKILL exists, need README |
| audit | Static + rubric report | Check without edits |
| fix | Minimal edits | Audit FAIL, same intent |

## When

### Use when

- Use when testing README static checks.

### Avoid when

- Do not use for production code review.

## Constraints

Self-invoke; static + reflection + pre-ship before write.

Source of truth: `SKILL.md`. This README is the human spec—not a Procedure echo.
"""

_ORCHESTRATOR_README_MISSING_ACTIONS = """\
# Test skill

One-line outcome sentence.

## Why

Problem and audience.

## What

Capabilities and boundaries.

## When

### Use when

- Use when testing README static checks.

### Avoid when

- Do not use for production code review.

## Constraints

Self-invoke; static + reflection + pre-ship before write.

Source of truth: `SKILL.md`. This README is the human spec—not a Procedure echo.
"""


def _write_artifact(plugin_root: Path, rel_path: str, body: str) -> str:
    target = plugin_root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return rel_path


def _load(plugin_root: Path, rel_path: str) -> AuditContext:
    loaded = AuditContext.load(plugin_root, rel_path)
    assert isinstance(loaded, AuditContext)
    return loaded


def _results_map(results: list[dict[str, str]]) -> dict[str, str]:
    return {item["id"]: item["result"] for item in results}


@pytest.mark.parametrize(
    ("fixture_body", "rel_path", "expected"),
    [
        (_VALID_SKILL, "skills/test-skill/SKILL.md", "PASS"),
        (
            _VALID_SKILL.replace("## Procedure\n\n1. Step one.\n", ""),
            "skills/test-skill/SKILL.md",
            "FAIL",
        ),
        (_VALID_COMMAND, "commands/test-cmd.md", "PASS"),
        (_VALID_AGENT, "agents/test-agent.md", "PASS"),
        (_VALID_RULE, "rules/test-rule.md", "PASS"),
        (_VALID_WORKFLOW, "docs/test-workflow.md", "PASS"),
        (_VALID_SKILL_README, "skills/test-skill/README.md", "PASS"),
    ],
)
def test_run_sections(
    tmp_path: Path,
    fixture_body: str,
    rel_path: str,
    expected: str,
) -> None:
    _write_artifact(tmp_path, rel_path, fixture_body)
    ctx = _load(tmp_path, rel_path)
    results = _results_map(run_sections(ctx))
    assert results["static.sections.required"] == expected


def test_run_orchestrator_readme_actions_required(tmp_path: Path) -> None:
    _write_artifact(tmp_path, "skills/test-skill/SKILL.md", _ORCHESTRATOR_SKILL)
    rel = _write_artifact(
        tmp_path,
        "skills/test-skill/README.md",
        _ORCHESTRATOR_README_MISSING_ACTIONS,
    )
    ctx = _load(tmp_path, rel)
    results = _results_map(run_sections(ctx))
    assert results["static.sections.required"] == "PASS"
    assert results["static.sections.orchestrator-actions"] == "FAIL"


def test_run_orchestrator_readme_actions_present(tmp_path: Path) -> None:
    _write_artifact(tmp_path, "skills/test-skill/SKILL.md", _ORCHESTRATOR_SKILL)
    rel = _write_artifact(
        tmp_path,
        "skills/test-skill/README.md",
        _ORCHESTRATOR_README_WITH_ACTIONS,
    )
    ctx = _load(tmp_path, rel)
    results = _results_map(run_sections(ctx))
    assert results["static.sections.orchestrator-actions"] == "PASS"


def test_run_sections_unknown_artifact_type_returns_empty(tmp_path: Path) -> None:
    rel = _write_artifact(tmp_path, "misc/unknown.md", "# Unknown\n\nNo sections.\n")
    ctx = _load(tmp_path, rel)
    assert ctx.artifact_type == "unknown"
    assert run_sections(ctx) == []


def test_run_sections_ref_file_returns_empty(tmp_path: Path) -> None:
    rel = _write_artifact(
        tmp_path,
        "skills/test-skill/refs/topic.md",
        "# Topic\n\nUnique constraints; no Purpose/Load/Content.\n",
    )
    ctx = _load(tmp_path, rel)
    assert ctx.artifact_type == "ref-file"
    assert run_sections(ctx) == []


def test_sibling_skill_missing_skips_orchestrator_actions(tmp_path: Path) -> None:
    rel = _write_artifact(
        tmp_path,
        "skills/test-skill/README.md",
        _ORCHESTRATOR_README_MISSING_ACTIONS,
    )
    ctx = _load(tmp_path, rel)
    results = _results_map(run_sections(ctx))
    assert "static.sections.orchestrator-actions" not in results
