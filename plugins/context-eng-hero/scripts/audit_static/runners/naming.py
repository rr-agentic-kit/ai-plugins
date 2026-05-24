from __future__ import annotations

import re

from audit_static.models import AuditContext, CheckResult
from audit_static.report import check

NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")


def run_naming(ctx: AuditContext) -> list[CheckResult]:
    results: list[CheckResult] = []
    name_val = (ctx.fm or {}).get("name", "")
    if ctx.artifact_type not in ("skill", "command", "agent") or not ctx.fm:
        return results

    ok_format = bool(NAME_RE.match(str(name_val)))
    results.append(
        check(
            "static.name.format",
            "critical",
            ok_format,
            f"name={name_val!r}" + ("" if ok_format else " (expected [a-z0-9-]{1,64})"),
        )
    )

    match ctx.artifact_type:
        case "skill":
            folder = ctx.rel.parts[1] if len(ctx.rel.parts) >= 2 else ""
            path_match = str(name_val) == folder
            results.append(
                check(
                    "static.name.path-match",
                    "critical",
                    path_match,
                    f"name={name_val!r} folder={folder!r}",
                )
            )
        case "command":
            stem = ctx.rel.stem
            path_match = str(name_val) == stem
            results.append(
                check(
                    "static.name.path-match",
                    "critical",
                    path_match,
                    f"name={name_val!r} stem={stem!r}",
                )
            )
    return results
