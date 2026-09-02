"""Unit tests for audit_static runner modules."""

from __future__ import annotations

from pathlib import Path

import pytest
from audit_static.models import AuditContext
from audit_static.runners.description import run_description
from audit_static.runners.frontmatter import run_frontmatter
from audit_static.runners.keys import run_keys
from audit_static.runners.links import run_links
from audit_static.runners.naming import run_naming
from audit_static.runners.paths import run_paths
from audit_static.runners.sections import run_sections
from audit_static.runners.workflow import run_ref_file, run_workflow


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


@pytest.mark.parametrize(
    ("fixture_body", "rel_path", "check_id", "expected"),
    [
        (
            _VALID_SKILL,
            "skills/test-skill/SKILL.md",
            "static.frontmatter.delimiters",
            "PASS",
        ),
        (
            _VALID_SKILL,
            "skills/test-skill/SKILL.md",
            "static.frontmatter.parseable",
            "PASS",
        ),
        (
            "# No frontmatter\n",
            "skills/bad-skill/SKILL.md",
            "static.frontmatter.delimiters",
            "FAIL",
        ),
        (
            _VALID_WORKFLOW,
            "workflows/test-workflow.md",
            "static.frontmatter.delimiters",
            "PASS",
        ),
    ],
)
def test_run_frontmatter(
    tmp_path: Path,
    fixture_body: str,
    rel_path: str,
    check_id: str,
    expected: str,
) -> None:
    # Arrange
    _write_artifact(tmp_path, rel_path, fixture_body)
    ctx = _load(tmp_path, rel_path)
    # Act
    results = _results_map(run_frontmatter(ctx))
    # Assert
    assert results[check_id] == expected


@pytest.mark.parametrize(
    ("fixture_body", "rel_path", "expected"),
    [
        (_VALID_SKILL, "skills/test-skill/SKILL.md", "PASS"),
        (
            "---\nname: test-skill\n---\n\n# Body\n",
            "skills/test-skill/SKILL.md",
            "FAIL",
        ),
        (_VALID_WORKFLOW, "workflows/test-workflow.md", None),
    ],
)
def test_run_keys(
    tmp_path: Path,
    fixture_body: str,
    rel_path: str,
    expected: str | None,
) -> None:
    # Arrange
    _write_artifact(tmp_path, rel_path, fixture_body)
    ctx = _load(tmp_path, rel_path)
    # Act
    results = run_keys(ctx)
    # Assert
    if expected is None:
        assert results == []
    else:
        assert _results_map(results)["static.keys.required"] == expected


@pytest.mark.parametrize(
    ("fixture_body", "rel_path", "check_id", "expected"),
    [
        (_VALID_SKILL, "skills/test-skill/SKILL.md", "static.name.format", "PASS"),
        (_VALID_SKILL, "skills/test-skill/SKILL.md", "static.name.path-match", "PASS"),
        (
            _VALID_SKILL.replace("test-skill", "WRONG"),
            "skills/test-skill/SKILL.md",
            "static.name.path-match",
            "FAIL",
        ),
        (_VALID_COMMAND, "commands/test-cmd.md", "static.name.path-match", "PASS"),
    ],
)
def test_run_naming(
    tmp_path: Path,
    fixture_body: str,
    rel_path: str,
    check_id: str,
    expected: str,
) -> None:
    # Arrange
    _write_artifact(tmp_path, rel_path, fixture_body)
    ctx = _load(tmp_path, rel_path)
    # Act
    results = _results_map(run_naming(ctx))
    # Assert
    assert results[check_id] == expected


@pytest.mark.parametrize(
    ("fixture_body", "rel_path", "check_id", "expected"),
    [
        (
            _VALID_SKILL,
            "skills/test-skill/SKILL.md",
            "static.description.present",
            "PASS",
        ),
        (
            "---\nname: test-skill\n---\n\n# Body\n",
            "skills/test-skill/SKILL.md",
            "static.description.present",
            "FAIL",
        ),
        (
            _VALID_SKILL.replace("Short valid skill description.", "x" * 1025),
            "skills/test-skill/SKILL.md",
            "static.description.max-length",
            "FAIL",
        ),
    ],
)
def test_run_description(
    tmp_path: Path,
    fixture_body: str,
    rel_path: str,
    check_id: str,
    expected: str,
) -> None:
    # Arrange
    _write_artifact(tmp_path, rel_path, fixture_body)
    ctx = _load(tmp_path, rel_path)
    # Act
    results = _results_map(run_description(ctx))
    # Assert
    assert results[check_id] == expected


@pytest.mark.parametrize(
    ("extra_line", "check_id", "expected"),
    [
        ("", "static.paths.no-parent-segment", "PASS"),
        ("See [ref](../escape.md).", "static.paths.no-parent-segment", "FAIL"),
        ("Deploy to /Users/dev/app.", "static.paths.no-absolute", "FAIL"),
    ],
)
def test_run_paths(
    tmp_path: Path,
    extra_line: str,
    check_id: str,
    expected: str,
) -> None:
    # Arrange
    body = _VALID_SKILL + (f"\n{extra_line}\n" if extra_line else "")
    rel = _write_artifact(tmp_path, "skills/test-skill/SKILL.md", body)
    ctx = _load(tmp_path, rel)
    # Act
    results = _results_map(run_paths(ctx))
    # Assert
    assert results[check_id] == expected


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
        (_VALID_WORKFLOW, "workflows/test-workflow.md", "PASS"),
        (_VALID_SKILL_README, "skills/test-skill/README.md", "PASS"),
    ],
)
def test_run_sections(
    tmp_path: Path,
    fixture_body: str,
    rel_path: str,
    expected: str,
) -> None:
    # Arrange
    _write_artifact(tmp_path, rel_path, fixture_body)
    ctx = _load(tmp_path, rel_path)
    # Act
    results = _results_map(run_sections(ctx))
    # Assert
    assert results["static.sections.required"] == expected


def test_run_skill_readme_frontmatter_optional(tmp_path: Path) -> None:
    rel = _write_artifact(tmp_path, "skills/test-skill/README.md", _VALID_SKILL_README)
    ctx = _load(tmp_path, rel)
    assert ctx.artifact_type == "skill-readme"
    results = _results_map(run_frontmatter(ctx))
    assert results["static.frontmatter.delimiters"] == "PASS"
    assert results["static.frontmatter.parseable"] == "PASS"


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


def test_run_links_pass_and_fail(tmp_path: Path) -> None:
    # Arrange — valid relative + https links
    good_body = (
        _VALID_SKILL
        + "\nSee [helper](refs/helper.md).\n"
        + "External [docs](https://example.com).\n"
    )
    helper_rel = "skills/test-skill/refs/helper.md"
    (tmp_path / helper_rel).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / helper_rel).write_text("# Helper\n", encoding="utf-8")
    good_rel = _write_artifact(tmp_path, "skills/test-skill/SKILL.md", good_body)
    good_ctx = _load(tmp_path, good_rel)

    bad_body = (
        _VALID_SKILL
        + "\nBroken [link](missing.md).\nInsecure [site](http://example.com).\n"
    )
    bad_rel = _write_artifact(tmp_path, "skills/bad-links/SKILL.md", bad_body)
    bad_ctx = _load(tmp_path, bad_rel)

    # Act
    good_results = _results_map(run_links(good_ctx))
    bad_results = _results_map(run_links(bad_ctx))

    # Assert
    assert good_results["static.links.internal-resolve"] == "PASS"
    assert good_results["static.links.https-only"] == "PASS"
    assert bad_results["static.links.internal-resolve"] == "FAIL"
    assert bad_results["static.links.https-only"] == "FAIL"


_VALID_REF_FILE = """\
# Helper ref

## Purpose

One falsifiable sentence.

## Load

Parent `skills/foo/SKILL.md` at Procedure step 2.

## Content

Unique constraints here.
"""

_VALID_WORKFLOW_WITH_TODO = """\
# Test workflow

## Outcome

Outcome text.

## Steps

| Step | todo_id | Owner artifact | Output contract |
|------|---------|----------------|-----------------|
| 1 | `wf-1-start` | skill | output |

## Delegation

Delegation.

## Exit and failure

Failure handling.

## Orchestration

Orchestration notes.
"""


def test_run_ref_file_sections(tmp_path: Path) -> None:
    rel = _write_artifact(tmp_path, "skills/foo/refs/helper.md", _VALID_REF_FILE)
    ctx = _load(tmp_path, rel)
    results = _results_map(run_ref_file(ctx))
    assert ctx.artifact_type == "ref-file"
    assert results["static.sections.required"] == "PASS"


def test_run_workflow_todo_id(tmp_path: Path) -> None:
    rel = _write_artifact(
        tmp_path, "workflows/test-workflow.md", _VALID_WORKFLOW_WITH_TODO
    )
    ctx = _load(tmp_path, rel)
    results = _results_map(run_workflow(ctx))
    assert results["static.workflow.todo-id"] == "PASS"


def test_run_workflow_todo_id_missing(tmp_path: Path) -> None:
    rel = _write_artifact(tmp_path, "workflows/bad-workflow.md", _VALID_WORKFLOW)
    ctx = _load(tmp_path, rel)
    results = _results_map(run_workflow(ctx))
    assert results["static.workflow.todo-id"] == "FAIL"
