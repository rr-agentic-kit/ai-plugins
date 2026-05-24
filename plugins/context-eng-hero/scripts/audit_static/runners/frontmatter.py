from __future__ import annotations

from audit_static.models import AuditContext, CheckResult
from audit_static.report import check


def run_frontmatter(ctx: AuditContext) -> list[CheckResult]:
    results: list[CheckResult] = []
    match ctx.artifact_type:
        case "workflow" if not ctx.has_fm:
            results.append(
                check(
                    "static.frontmatter.delimiters",
                    "critical",
                    True,
                    "workflow: frontmatter optional",
                )
            )
            results.append(
                check(
                    "static.frontmatter.parseable",
                    "critical",
                    True,
                    "workflow: no frontmatter required",
                )
            )
        case _:
            delimiter_ok = ctx.has_fm and ctx.fm_err not in (
                "missing opening --- delimiter",
                "missing closing --- delimiter",
            )
            results.append(
                check(
                    "static.frontmatter.delimiters",
                    "critical",
                    delimiter_ok,
                    (
                        "bounded by --- lines"
                        if delimiter_ok
                        else (ctx.fm_err or "no frontmatter")
                    ),
                )
            )
            results.append(
                check(
                    "static.frontmatter.parseable",
                    "critical",
                    ctx.fm is not None,
                    (
                        "YAML parsed"
                        if ctx.fm is not None
                        else (ctx.fm_err or "unparseable")
                    ),
                )
            )
    return results
