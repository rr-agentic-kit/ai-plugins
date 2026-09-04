from __future__ import annotations

from audit_static.models import AuditContext, CheckResult
from audit_static.report import check

_REQUIRED_KEYS: dict[str, list[str]] = {
    "skill": ["name", "description"],
    "command": ["name", "description"],
    "agent": ["name", "description"],
    "rule": ["description"],
}


def run_keys(ctx: AuditContext) -> list[CheckResult]:
    if ctx.artifact_type in {"workflow", "skill-readme", "ref-file", "unknown"}:
        return []
    keys = _REQUIRED_KEYS.get(ctx.artifact_type, [])
    missing = [
        k for k in keys if not ctx.fm or k not in ctx.fm or ctx.fm[k] in (None, "")
    ]
    return [
        check(
            "static.keys.required",
            "critical",
            not missing,
            "all present" if not missing else f"missing: {', '.join(missing)}",
        )
    ]
