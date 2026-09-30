"""Accumulate lean tool events into session scratch."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .constants import MAX_USER_TEXT, TOOL_READ
from .gates import is_local_source_skill, looks_like_skill_md
from .redact import redact_secrets
from .score import fingerprint_cmd
from .store import append_event, ensure_session, load_state, save_state


def _extract_tool_name(data: dict[str, Any]) -> str:
    for key in ("tool_name", "toolName", "tool", "name"):
        val = data.get(key)
        if val:
            return str(val)
    tool_input = data.get("tool_input") or data.get("toolInput") or {}
    if isinstance(tool_input, dict) and tool_input.get("name"):
        return str(tool_input["name"])
    return ""


def _extract_path(data: dict[str, Any]) -> str | None:
    for key in ("file_path", "filePath", "path"):
        val = data.get(key)
        if val:
            return str(val)
    tool_input = data.get("tool_input") or data.get("toolInput") or {}
    if isinstance(tool_input, dict):
        for key in ("file_path", "filePath", "path", "target_file", "notebook_path"):
            nested = tool_input.get(key)
            if nested:
                return str(nested)
    return None


def _extract_command(data: dict[str, Any]) -> str | None:
    for key in ("command", "cmd"):
        val = data.get(key)
        if val:
            return str(val)
    tool_input = data.get("tool_input") or data.get("toolInput") or {}
    if isinstance(tool_input, dict):
        for key in ("command", "cmd"):
            nested = tool_input.get(key)
            if nested:
                return str(nested)
    return None


def build_event(
    data: dict[str, Any],
    *,
    failed: bool = False,
) -> dict[str, Any]:
    tool = _extract_tool_name(data)
    raw_path = _extract_path(data)
    path = redact_secrets(raw_path) if raw_path else None
    cmd = _extract_command(data)
    cmd_fp = fingerprint_cmd(cmd) if cmd else None
    fingerprint = path or (cmd_fp or "")
    return {
        "ts": time.time(),
        "tool": tool,
        "fingerprint": fingerprint,
        "path": path,
        "cmd": cmd_fp,
        "failed": failed,
        "ok": not failed,
    }


def maybe_bind_skill(
    state: dict[str, Any],
    path: str | None,
    roots: list[str],
) -> dict[str, Any]:
    """Set bound_skill + absorb_into when Read of local source SKILL.md."""
    if not path or not looks_like_skill_md(path):
        return state
    if not is_local_source_skill(path, roots):
        return state
    # Prefer first bind; allow upgrade if previously unbound.
    if state.get("bound_skill") and Path(str(state["bound_skill"])) == Path(path):
        return state
    if state.get("bound_skill") and is_local_source_skill(
        str(state["bound_skill"]), roots
    ):
        return state
    state = dict(state)
    state["bound_skill"] = path
    state["absorb_into"] = path
    return state


def accumulate(
    *,
    workspace: Path,
    session_id: str,
    data: dict[str, Any],
    roots: list[str],
    failed: bool = False,
    user_text: str | None = None,
) -> bool:
    """
    Append event + refresh state. Returns False on IO failure (fail-open caller).
    """
    session = ensure_session(workspace, session_id)
    if session is None:
        return False
    event = build_event(data, failed=failed)
    if not append_event(session, event):
        return False
    state = load_state(session)
    if user_text:
        scrubbed = redact_secrets(user_text)
        if len(scrubbed) > MAX_USER_TEXT:
            suffix = "\n…(truncated)"
            scrubbed = scrubbed[: max(0, MAX_USER_TEXT - len(suffix))] + suffix
        state["last_user_text"] = scrubbed
    path = event.get("path")
    if isinstance(path, str) and event.get("tool") == TOOL_READ:
        state = maybe_bind_skill(state, path, roots)
    return save_state(session, state)
