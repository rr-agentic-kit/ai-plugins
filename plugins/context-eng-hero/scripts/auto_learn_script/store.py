"""Session scratch under .ai/learning/ce-auto-learn/<session_id>/."""

from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path
from typing import Any

from .constants import (
    EVENTS_NAME,
    MAX_EVENTS,
    MAX_EVENTS_BYTES,
    ORPHAN_TTL_DAYS,
    SCRATCH_REL,
    STATE_NAME,
)

_ALLOWED_SESSION_FILES = frozenset({EVENTS_NAME, STATE_NAME})


def session_dir(workspace: Path, session_id: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in session_id)[:128]
    if not safe:
        safe = "unknown"
    return workspace / SCRATCH_REL / safe


def _session_file(session: Path, name: str) -> Path | None:
    """Allowlisted basename under session root (S2083/S8707 sanitizer)."""
    if name not in _ALLOWED_SESSION_FILES or Path(name).name != name:
        return None
    try:
        root = Path(os.path.realpath(session))
        target = Path(os.path.realpath(root / name))
    except OSError:
        return None
    root_s = str(root)
    target_s = str(target)
    if target_s != root_s and not target_s.startswith(f"{root_s}{os.sep}"):
        return None
    if target.parent != root:
        return None
    return target


def ensure_session(workspace: Path, session_id: str) -> Path | None:
    """Create session scratch. None on mkdir failure (fail-open)."""
    path = session_dir(workspace, session_id)
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None
    return path


def load_state(session: Path) -> dict[str, Any]:
    path = _session_file(session, STATE_NAME)
    if path is None or not path.is_file():
        return _empty_state()
    try:
        with open(str(path), encoding="utf-8") as fh:
            data = json.loads(fh.read())
    except OSError, json.JSONDecodeError:
        return _empty_state()
    if not isinstance(data, dict):
        return _empty_state()
    base = _empty_state()
    base.update(data)
    return base


def save_state(session: Path, state: dict[str, Any]) -> bool:
    path = _session_file(session, STATE_NAME)
    if path is None:
        return False
    try:
        with open(str(path), "w", encoding="utf-8") as fh:
            fh.write(json.dumps(state, indent=2) + "\n")
    except OSError:
        return False
    return True


def append_event(session: Path, event: dict[str, Any]) -> bool:
    """Append one JSONL event; enforce MAX_EVENTS / MAX_EVENTS_BYTES caps."""
    path = _session_file(session, EVENTS_NAME)
    if path is None:
        return False
    line = json.dumps(event, separators=(",", ":")) + "\n"
    try:
        with open(str(path), "a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError:
        return False
    return _trim_events(session)


def _trim_events(session: Path) -> bool:
    """Keep the newest MAX_EVENTS lines and stay under MAX_EVENTS_BYTES."""
    path = _session_file(session, EVENTS_NAME)
    if path is None:
        return False
    try:
        with open(str(path), encoding="utf-8") as fh:
            raw = fh.read()
    except OSError:
        return False
    lines = [ln for ln in raw.splitlines() if ln.strip()]
    if len(lines) <= MAX_EVENTS and len(raw.encode("utf-8")) <= MAX_EVENTS_BYTES:
        return True
    kept = lines[-MAX_EVENTS:]
    # Drop oldest until under byte budget (newest-first retention).
    while kept and len(("\n".join(kept) + "\n").encode("utf-8")) > MAX_EVENTS_BYTES:
        kept = kept[1:]
    try:
        with open(str(path), "w", encoding="utf-8") as fh:
            fh.write(("\n".join(kept) + "\n") if kept else "")
    except OSError:
        return False
    return True


def load_events(session: Path) -> list[dict[str, Any]]:
    path = _session_file(session, EVENTS_NAME)
    if path is None or not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    try:
        with open(str(path), encoding="utf-8") as fh:
            text = fh.read()
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
