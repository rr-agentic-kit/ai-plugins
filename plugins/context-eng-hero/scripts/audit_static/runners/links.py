from __future__ import annotations

from audit_static.links import collect_broken_links, collect_insecure_http_links
from audit_static.models import AuditContext, CheckResult
from audit_static.report import check


def run_links(ctx: AuditContext) -> list[CheckResult]:
    broken = collect_broken_links(ctx)
    insecure = collect_insecure_http_links(ctx)
    if not broken:
        broken_message = "all relative links resolve"
    else:
        broken_suffix = " ..." if len(broken) > 5 else ""
        broken_message = f"broken: {', '.join(broken[:5])}{broken_suffix}"
    if not insecure:
        insecure_message = "no insecure http links"
    else:
        insecure_suffix = " ..." if len(insecure) > 5 else ""
        insecure_message = f"insecure http: {', '.join(insecure[:5])}{insecure_suffix}"
    return [
        check(
            "static.links.internal-resolve",
            "major",
            not broken,
            broken_message,
        ),
        check(
            "static.links.https-only",
            "critical",
            not insecure,
            insecure_message,
        ),
    ]
