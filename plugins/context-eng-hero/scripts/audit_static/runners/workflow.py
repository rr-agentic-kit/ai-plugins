from __future__ import annotations

import re

from audit_static.models import AuditContext, CheckResult
from audit_static.report import check

_TODO_ID_CELL = re.compile(r"`[a-z0-9][a-z0-9-]*`")


def _todo_ids_from_steps_body(body: str) -> list[str]:
    in_steps = False
    todo_ids: list[str] = []
    for line in body.splitlines():
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
    return todo_ids


def _workflow_todo_detail(todo_ids: list[str]) -> tuple[bool, str]:
    has_todo = len(todo_ids) > 0
    unique = len(todo_ids) == len(set(todo_ids))
    ok = has_todo and unique
    if not has_todo:
        return ok, "no todo_id values in Steps table"
    if not unique:
        return ok, "duplicate todo_id values in Steps table"
    return ok, f"found {len(todo_ids)} todo_id value(s)"


def run_workflow(ctx: AuditContext) -> list[CheckResult]:
    if ctx.artifact_type != "workflow":
        return []

    todo_ids = _todo_ids_from_steps_body(ctx.body)
    ok, detail = _workflow_todo_detail(todo_ids)
    return [
        check(
            "static.workflow.todo-id",
            "critical",
            ok,
            detail,
        )
    ]
