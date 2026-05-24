from __future__ import annotations

import re

from audit_static.models import AuditContext, CheckResult
from audit_static.report import check

ABS_PATH_RE = re.compile(
    r"(?:^|[\s(])(?:/[A-Za-z0-9._-]+|~/)|"
    r"[A-Za-z]:\\|"
    r"(?:^|[\s(])/(?:Users|home|var|etc|tmp|opt)/"
)
PARENT_SEGMENT_RE = re.compile(r"\.\./|\.\.\\")


def run_paths(ctx: AuditContext) -> list[CheckResult]:
    no_parent = PARENT_SEGMENT_RE.search(ctx.text) is None
    no_abs = ABS_PATH_RE.search(ctx.text) is None
    return [
        check(
            "static.paths.no-parent-segment",
            "critical",
            no_parent,
            "no .. segments" if no_parent else "contains .. path segment",
        ),
        check(
            "static.paths.no-absolute",
            "major",
            no_abs,
            "no absolute paths" if no_abs else "absolute path pattern found",
        ),
    ]
