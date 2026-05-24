from __future__ import annotations

from audit_static.headings import headings_present
from audit_static.models import AuditContext, CheckResult
from audit_static.report import check

SKILL_SECTIONS = {"Purpose", "When to use", "Procedure"}
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
    "command": COMMAND_SECTIONS,
    "agent": AGENT_SECTIONS,
    "rule": RULE_SECTIONS,
    "workflow": WORKFLOW_SECTIONS,
}


def run_sections(ctx: AuditContext) -> list[CheckResult]:
    present = headings_present(ctx.body)
    required_secs = _SECTION_MAP[ctx.artifact_type]
    missing_secs = sorted(required_secs - present)
    return [
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
