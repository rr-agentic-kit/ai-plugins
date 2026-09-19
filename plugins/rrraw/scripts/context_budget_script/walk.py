"""Walk plan dirs and resolve linked markdown/yaml docs."""

from __future__ import annotations

import re
from pathlib import Path

from .constants import LINK_EXTS, is_plan_markdown

_MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_BARE_PATH = re.compile(
    r"(?:^|\s)((?:\./|\.\./)?(?:deltas/|constitution/|adrs/)?"
    r"[\w./-]+\.(?:md|ya?ml))",
    re.MULTILINE,
)


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def collect_plan_markdown(plan_dir: Path) -> list[Path]:
    """All `.md` under plan_dir (recursive), sorted."""
    if not plan_dir.is_dir():
        return []
    found = sorted(p for p in plan_dir.rglob("*.md") if p.is_file())
    return found


def extract_linked_paths(text: str, base: Path) -> list[Path]:
    """Resolve relative links from markdown/yaml text next to base file."""
    candidates: list[str] = []
    candidates.extend(_MD_LINK.findall(text))
    candidates.extend(m.group(1) for m in _BARE_PATH.finditer(text))
    out: list[Path] = []
    seen: set[Path] = set()
    for raw in candidates:
        href = raw.strip().strip("\"'")
        if not href or href.startswith(("http://", "https://", "#", "mailto:")):
            continue
        href = href.split("#", 1)[0].split("?", 1)[0]
        if not href:
            continue
        path = (base.parent / href).resolve()
        if path.suffix.lower() not in LINK_EXTS:
            continue
        if not path.is_file() or path in seen:
            continue
        seen.add(path)
        out.append(path)
    return out


def collect_plan_and_linked(plan_dir: Path) -> list[Path]:
    """Plan markdown plus explicitly linked docs under/near the plan tree."""
    plan_dir = plan_dir.resolve()
    files = collect_plan_markdown(plan_dir)
    seen = set(files)
    queue = list(files)
    while queue:
        current = queue.pop(0)
        text = _read_text(current)
        if text is None:
            continue
        for linked in extract_linked_paths(text, current):
            if linked in seen:
                continue
            # Keep linked docs that live under plan_dir or are plan markdown.
            try:
                linked.relative_to(plan_dir)
                in_tree = True
            except ValueError:
                in_tree = is_plan_markdown(linked)
            if not in_tree and linked.suffix.lower() != ".md":
                continue
            if not in_tree and not is_plan_markdown(linked):
                # Allow sibling constitution shards / explicit relative md under docs/rr
                norm = linked.as_posix().lower()
                if "/docs/rr/" not in norm:
                    continue
            seen.add(linked)
            files.append(linked)
            if linked.suffix.lower() == ".md":
                queue.append(linked)
    return sorted(files)
