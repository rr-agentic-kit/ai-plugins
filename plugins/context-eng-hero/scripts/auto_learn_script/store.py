"""Session scratch under .ai/learning/ce-auto-learn/<session_id>/."""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Any

from .constants import EVENTS_NAME, ORPHAN_TTL_DAYS, SCRATCH_REL, STATE_NAME


def session_dir(workspace: Path, session_id: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in session_id)[:128]
    if not safe:
        safe = "unknown"
    return workspace / SCRATCH_REL / safe


def ensure_session(workspace: Path, session_id: str) -> Path | None:
    """Create session scratch. None on mkdir failure (fail-open)."""
    path = session_dir(workspace, session_id)
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None
    return path


def events_path(session: Path) -> Path:
    return session / EVENTS_NAME


def state_path(session: Path) -> Path:
    return session / STATE_NAME


def load_state(session: Path) -> dict[str, Any]:
    path = state_path(session)
    if not path.is_file():
        return _empty_state()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError, json.JSONDecodeError:
        return _empty_state()
    if not isinstance(data, dict):
        return _empty_state()
    base = _empty_state()
    base.update(data)
    return base


def save_state(session: Path, state: dict[str, Any]) -> bool:
    path = state_path(session)
    try:
        path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    except OSError:
        return False
    return True


def append_event(session: Path, event: dict[str, Any]) -> bool:
    path = events_path(session)
    try:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, separators=(",", ":")) + "\n")
    except OSError:
        return False
    return True


def load_events(session: Path) -> list[dict[str, Any]]:
    path = events_path(session)
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def mark_consumed(session: Path) -> bool:
    state = load_state(session)
    state["consumed"] = True
    state["consumed_at"] = time.time()
    return save_state(session, state)


def delete_session(workspace: Path, session_id: str) -> None:
    path = session_dir(workspace, session_id)
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)


def purge_orphans(workspace: Path, *, ttl_days: int = ORPHAN_TTL_DAYS) -> int:
    """Delete session dirs older than TTL. Returns count removed."""
    root = workspace / SCRATCH_REL
    if not root.is_dir():
        return 0
    cutoff = time.time() - ttl_days * 86400
    removed = 0
    try:
        children = list(root.iterdir())
    except OSError:
        return 0
    for child in children:
        if not child.is_dir():
            continue
        try:
            mtime = child.stat().st_mtime
        except OSError:
            continue
        if mtime < cutoff:
            shutil.rmtree(child, ignore_errors=True)
            removed += 1
    return removed


def _empty_state() -> dict[str, Any]:
    return {
        "bound_skill": None,
        "absorb_into": None,
        "consumed": False,
        "signals": {},
        "last_user_text": None,
    }
