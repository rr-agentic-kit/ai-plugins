from __future__ import annotations

from audit_static.links import collect_broken_links
from audit_static.models import AuditContext, CheckResult
from audit_static.report import check


def run_links(ctx: AuditContext) -> list[CheckResult]:
    broken = collect_broken_links(ctx)
    return [
        check(
            "static.links.internal-resolve",
            "major",
            not broken,
            (
                "all relative links resolve"
                if not broken
                else f"broken: {', '.join(broken[:5])}"
                + (" ..." if len(broken) > 5 else "")
            ),
        )
    ]
