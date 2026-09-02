from __future__ import annotations

import re

from audit_static.headings import headings_present
from audit_static.models import AuditContext, CheckResult
from audit_static.report import check

REF_FILE_SECTIONS = {"Purpose", "Load", "Content"}
_TODO_ID_CELL = re.compile(r"`[a-z0-9][a-z0-9-]*`")


def run_ref_file(ctx: AuditContext) -> list[CheckResult]:
    if ctx.artifact_type != "ref-file":
        return []
    present = headings_present(ctx.body)
    missing_secs = sorted(REF_FILE_SECTIONS - present)
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


def run_workflow(ctx: AuditContext) -> list[CheckResult]:
    if ctx.artifact_type != "workflow":
        return []

    results: list[CheckResult] = []
    in_steps = False
    todo_ids: list[str] = []
    for line in ctx.body.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_steps = stripped == "## Steps"
            continue
        if not in_steps or not stripped.startswith("|"):
            continue
        if stripped.startswith("|--") or "todo_id" in stripped.lower():
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 2:
            continue
        match = _TODO_ID_CELL.search(cells[1])
        if match:
            todo_ids.append(match.group(0).strip("`"))

    has_todo = len(todo_ids) > 0
    unique = len(todo_ids) == len(set(todo_ids))
    ok = has_todo and unique
    detail = (
        f"found {len(todo_ids)} todo_id value(s)"
        if has_todo
        else "no todo_id values in Steps table"
    )
    if has_todo and not unique:
        detail = "duplicate todo_id values in Steps table"
    results.append(
        check(
            "static.workflow.todo-id",
            "critical",
            ok,
            detail,
        )
    )
    return results
