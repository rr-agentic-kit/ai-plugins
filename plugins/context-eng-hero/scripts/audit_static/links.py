from __future__ import annotations

import re
from pathlib import Path

from audit_static.models import AuditContext

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def resolve_link(plugin_root: Path, source: Path, target: str) -> bool:
    t = target.strip()
    if not t or t.startswith(("http://", "https://", "mailto:", "#")):
        return True
    if "://" in t:
        return True
    base = source.parent if source.is_file() else plugin_root
    candidate = (base / t.split("#")[0]).resolve()
    try:
        candidate.relative_to(plugin_root.resolve())
    except ValueError:
        return False
    return candidate.exists()


def collect_broken_links(ctx: AuditContext) -> list[str]:
    broken: list[str] = []
    for _label, href in LINK_RE.findall(ctx.body):
        if not resolve_link(ctx.plugin_root, ctx.target, href):
            broken.append(href)
    return broken
