from __future__ import annotations

import re

from audit_static.headings import headings_present
from audit_static.models import AuditContext, CheckResult
from audit_static.report import check

SKILL_SECTIONS = {"Purpose", "When to use", "Procedure"}
SKILL_README_SECTIONS = {"Why", "What", "When"}
COMMAND_SECTIONS = {"Input contract", "Execution", "Output"}
AGENT_SECTIONS = {"Role", "Tools and boundaries", "Stop conditions", "Outputs"}
RULE_SECTIONS = {"Intent", "Requirements", "Scope", "Exceptions"}
WORKFLOW_SECTIONS = {
    "Outcome",
    "Steps",
    "Delegation",
    "Exit and failure",
    "Orchestration",
}

_SECTION_MAP = {
    "skill": SKILL_SECTIONS,
    "skill-readme": SKILL_README_SECTIONS,
    "command": COMMAND_SECTIONS,
    "agent": AGENT_SECTIONS,
    "rule": RULE_SECTIONS,
    "workflow": WORKFLOW_SECTIONS,
    "ref-file": set(),  # handled by run_ref_file
}

_ACTIONS_SECTION_RE = re.compile(
    r"^## Actions\s*\n(.*)(?=(?:^## |\Z))",
    re.MULTILINE | re.DOTALL,
)
_ACTION_TABLE_DATA_ROW_RE = re.compile(
    r"^\| ([^|]+) \|",
    re.MULTILINE,
)


def _sibling_skill_text(ctx: AuditContext) -> str | None:
    parts = ctx.rel.parts
    if len(parts) < 3 or parts[0] != "skills" or ctx.rel.name.lower() != "readme.md":
        return None
    skill_path = ctx.plugin_root / parts[0] / parts[1] / "SKILL.md"
    if not skill_path.is_file():
        return None
    return skill_path.read_text(encoding="utf-8")


def _is_orchestrator_skill(skill_text: str) -> bool:
    match = _ACTIONS_SECTION_RE.search(skill_text)
    if not match:
        return False
    section = match.group(1)
    data_rows = 0
    for row in _ACTION_TABLE_DATA_ROW_RE.finditer(section):
        first_cell = row.group(1).strip()
        if first_cell.startswith("-") or first_cell.lower() == "action":
            continue
        if first_cell.lower() in {"action id", "action"}:
            continue
        data_rows += 1
    return data_rows >= 3


def run_sections(ctx: AuditContext) -> list[CheckResult]:
    required_secs = _SECTION_MAP.get(ctx.artifact_type)
    if required_secs is None:
        return []
    present = headings_present(ctx.body)
    missing_secs = sorted(required_secs - present)
    results = [
        check(
            "static.sections.required",
            "critical",
            not missing_secs,
            (
                "all required ## headings present"
                if not missing_secs
                else f"missing: {', '.join(missing_secs)}"
            ),
        )
    ]

    if ctx.artifact_type != "skill-readme":
        return results

    skill_text = _sibling_skill_text(ctx)
    if skill_text is None or not _is_orchestrator_skill(skill_text):
        return results

    has_actions = "Actions" in present
    results.append(
        check(
            "static.sections.orchestrator-actions",
            "critical",
            has_actions,
            (
                "Actions section present for orchestrator skill"
                if has_actions
                else "missing: Actions (orchestrator skill)"
            ),
        )
    )
    return results
