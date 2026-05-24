from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

from audit_static.models import AuditContext

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def link_scheme(target: str) -> str | None:
    t = target.strip()
    if "://" in t:
        scheme = urlparse(t).scheme
        return scheme.lower() if scheme else None
    colon = t.find(":")
    if colon > 0:
        prefix = t[:colon]
        if prefix.isalpha():
            return prefix.lower()
    return None


def is_insecure_http_link(target: str) -> bool:
    return link_scheme(target) == "http"


def collect_insecure_http_links(ctx: AuditContext) -> list[str]:
    insecure: list[str] = []
    for _label, href in LINK_RE.findall(ctx.body):
        if is_insecure_http_link(href):
            insecure.append(href)
    return insecure


def resolve_link(plugin_root: Path, source: Path, target: str) -> bool:
    t = target.strip()
    if not t or t.startswith("#"):
        return True
    if link_scheme(t) is not None:
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
        if is_insecure_http_link(href):
            continue
        if not resolve_link(ctx.plugin_root, ctx.target, href):
            broken.append(href)
    return broken
