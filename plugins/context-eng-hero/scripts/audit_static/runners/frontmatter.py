from __future__ import annotations

from audit_static.models import AuditContext, CheckResult
from audit_static.report import check

FM_DELIMITERS = "static.frontmatter.delimiters"
FM_PARSEABLE = "static.frontmatter.parseable"


def run_frontmatter(ctx: AuditContext) -> list[CheckResult]:
    results: list[CheckResult] = []
    match ctx.artifact_type:
        case "workflow" | "skill-readme" if not ctx.has_fm:
            label = "workflow" if ctx.artifact_type == "workflow" else "skill-readme"
            results.append(
                check(
                    FM_DELIMITERS,
                    "critical",
                    True,
                    f"{label}: frontmatter optional",
                )
            )
            results.append(
                check(
                    FM_PARSEABLE,
                    "critical",
                    True,
                    f"{label}: no frontmatter required",
                )
            )
        case "skill-readme" if ctx.has_fm:
            delimiter_ok = ctx.fm_err not in (
                "missing opening --- delimiter",
                "missing closing --- delimiter",
            )
            results.append(
                check(
                    FM_DELIMITERS,
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
                    FM_PARSEABLE,
                    "critical",
                    ctx.fm is not None,
                    (
                        "YAML parsed"
                        if ctx.fm is not None
                        else (ctx.fm_err or "unparseable")
                    ),
                )
            )
        case _:
            delimiter_ok = ctx.has_fm and ctx.fm_err not in (
                "missing opening --- delimiter",
                "missing closing --- delimiter",
            )
            results.append(
                check(
                    FM_DELIMITERS,
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
                    FM_PARSEABLE,
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
