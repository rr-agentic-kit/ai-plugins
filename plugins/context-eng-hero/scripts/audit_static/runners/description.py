from __future__ import annotations

from audit_static.models import AuditContext, CheckResult
from audit_static.report import check


def run_description(ctx: AuditContext) -> list[CheckResult]:
    if ctx.artifact_type == "workflow":
        return []

    desc = (ctx.fm or {}).get("description", "")
    has_desc = bool(str(desc).strip())
    results = [
        check(
            "static.description.present",
            "critical",
            has_desc,
            "description set" if has_desc else "description missing or empty",
        )
    ]
    if ctx.artifact_type == "skill" and has_desc:
        ok_len = len(str(desc)) <= 1024
        results.append(
            check(
                "static.description.max-length",
                "major",
                ok_len,
                f"length={len(str(desc))} (max 1024)",
            )
        )
    return results
