"""Local-directories gate: bind only writable source skills, never cache."""

from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path

from .constants import CACHE_MARKERS, SKILL_MD_RE


def _norm(path: Path | str) -> str:
    text = str(path).replace("\\", "/")
    try:
        text = Path(text).expanduser().resolve().as_posix()
    except OSError:
        text = Path(text).expanduser().as_posix()
    return text


def is_cache_path(path: Path | str) -> bool:
    """True when path sits under Claude/Cursor plugin runtime caches."""
    norm = _norm(path).lower()
    home = Path.home().as_posix().lower()
    markers = list(CACHE_MARKERS)
    # Also match home-relative forms without leading slash quirks.
    markers.extend(
        [
            f"{home}/.claude/plugins/cache/",
            f"{home}/.cursor/plugins/cache/",
        ]
    )
    return any(m in norm for m in markers)


def under_roots(path: Path | str, roots: Sequence[Path | str]) -> bool:
    """True when path is under any workspace/cwd root."""
    if not roots:
        return False
    target = _norm(path)
    for root in roots:
        try:
            root_n = _norm(root)
        except OSError:
            continue
        if target == root_n or target.startswith(root_n.rstrip("/") + "/"):
            return True
    return False


def looks_like_skill_md(path: Path | str) -> bool:
    """Prefer plugins/<name>/skills/<skill>/SKILL.md and project skill roots."""
    norm = _norm(path)
    return bool(SKILL_MD_RE.search(norm))


def is_local_source_skill(
    path: Path | str,
    roots: Sequence[Path | str],
) -> bool:
    """
    Fire inject only when evidence binds a skill whose SKILL.md is:
    - under workspace / cwd tree, and
    - not under runtime caches.
    """
    if not looks_like_skill_md(path):
        return False
    if is_cache_path(path):
        return False
    return under_roots(path, roots)


def default_workspace_roots(
    payload_roots: list[str] | None = None,
    *,
    cwd: str | None = None,
) -> list[str]:
    """Resolve workspace roots from hook payload, env, or process cwd."""
    roots: list[str] = []
    if payload_roots:
        roots.extend(str(r) for r in payload_roots if r)
    if cwd:
        roots.append(cwd)
    env_cwd = os.environ.get("CURSOR_PROJECT_DIR") or os.environ.get(
        "CLAUDE_PROJECT_DIR"
    )
    if env_cwd:
        roots.append(env_cwd)
    if not roots:
        roots.append(str(Path.cwd()))
    # Dedupe while preserving order.
    seen: set[str] = set()
    out: list[str] = []
    for r in roots:
        key = _norm(r)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out
