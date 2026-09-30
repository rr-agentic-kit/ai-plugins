"""Dual-runtime hook adapter: accumulate / score / inject / cleanup."""

from __future__ import annotations

import contextlib
import json
from pathlib import Path
from typing import Any

from .accumulate import accumulate
from .gates import default_workspace_roots, is_local_source_skill
from .inject import build_inject_message, emit_stop_payload
from .score import SignalHit, meets_inject_bar, score_events
from .store import (
    delete_session,
    load_events,
    load_state,
    mark_consumed,
    purge_orphans,
    session_dir,
)


def parse_hook_payload(raw: str) -> dict[str, Any] | None:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def _event_name(data: dict[str, Any]) -> str:
    name = (
        data.get("hook_event_name")
        or data.get("hookEventName")
        or data.get("event")
        or ""
    )
    return str(name)


def _session_id(data: dict[str, Any]) -> str:
    for key in ("session_id", "sessionId", "conversation_id", "conversationId"):
        val = data.get(key)
        if val:
            return str(val)
    return "default"


def _workspace(data: dict[str, Any], roots: list[str]) -> Path:
    if roots:
        return Path(roots[0])
    cwd = data.get("cwd")
    if cwd:
        return Path(str(cwd))
    return Path.cwd()


def _payload_roots(data: dict[str, Any]) -> list[str]:
    roots = data.get("workspace_roots") or data.get("workspaceRoots") or []
    if isinstance(roots, str):
        roots = [roots]
    cwd = data.get("cwd")
    out = [str(r) for r in roots]
    if cwd:
        out.append(str(cwd))
    return out


def _is_stop_event(name: str, runtime: str) -> bool:
    del runtime
    return name.lower() == "stop"


def _is_session_end(name: str) -> bool:
    return name.lower() in ("sessionend", "session_end")


def _is_tool_failure(name: str, data: dict[str, Any]) -> bool:
    n = name.lower()
    if "failure" in n or n.endswith("fail"):
        return True
    return bool(data.get("failed") or data.get("error"))


def _is_tool_event(name: str, runtime: str) -> bool:
    del runtime
    n = name.lower()
    return n in (
        "posttooluse",
        "posttoolusefailure",
        "aftertooluse",
    ) or ("tool" in n and "stop" not in n)


def _reentry_blocked(data: dict[str, Any], state: dict[str, Any]) -> bool:
    """Consumed marker, stop_hook_active, or loop_count ≥ 1 → no second inject."""
    if state.get("consumed"):
        return True
    if data.get("stop_hook_active") is True:
        return True
    loop = data.get("loop_count") or data.get("loopCount")
    try:
        if loop is not None and int(loop) >= 1:
            return True
    except TypeError, ValueError:
        pass
    return False


def evaluate_stop(
    *,
    workspace: Path,
    session_id: str,
    data: dict[str, Any],
    roots: list[str],
) -> tuple[str, list[SignalHit]] | None:
    """
    Return (message, hits) when inject bar is met; else None.
    """
    session = session_dir(workspace, session_id)
    if not session.is_dir():
        return None
    state = load_state(session)
    if _reentry_blocked(data, state):
        return None
    bound = state.get("bound_skill")
    absorb = state.get("absorb_into") or bound
    if not bound or not absorb:
        return None
    if not is_local_source_skill(str(bound), roots):
        return None
    if not is_local_source_skill(str(absorb), roots):
        return None
    events = load_events(session)
    hits = score_events(
        events,
        skill_bound=True,
        last_user_text=state.get("last_user_text"),
    )
    # Allow payload to carry last user text for correction signal.
    if not state.get("last_user_text"):
        prompt = data.get("last_user_message") or data.get("user_message") or ""
        if prompt:
            hits = score_events(
                events,
                skill_bound=True,
                last_user_text=str(prompt),
            )
    if not meets_inject_bar(hits):
        return None
    message = build_inject_message(
        bound_skill=str(bound),
        absorb_into=str(absorb),
        signals=hits,
    )
    return message, hits


def _accumulate_tool_event(
    *,
    workspace: Path,
    session_id: str,
    data: dict[str, Any],
    roots: list[str],
    event: str,
) -> None:
    failed = _is_tool_failure(event, data)
    user_text = None
    for key in ("user_message", "last_user_message", "prompt"):
        if data.get(key):
            user_text = str(data[key])
            break
    accumulate(
        workspace=workspace,
        session_id=session_id,
        data=data,
        roots=roots,
        failed=failed,
        user_text=user_text,
    )


def _has_tool_fields(data: dict[str, Any]) -> bool:
    return bool(
        data.get("tool_name")
        or data.get("toolName")
        or data.get("tool_input")
        or data.get("toolInput")
        or data.get("file_path")
        or data.get("filePath")
    )


def run_hook(*, runtime: str, stdin_text: str) -> str | None:
    """Return inject JSON string, or None for silent (fail-open)."""
    if runtime not in ("cursor", "claude"):
        return None
    data = parse_hook_payload(stdin_text)
    if data is None:
        return None

    roots = default_workspace_roots(
        _payload_roots(data),
        cwd=str(data["cwd"]) if data.get("cwd") else None,
    )
    workspace = _workspace(data, roots)
    session_id = _session_id(data)
    event = _event_name(data)

    # Opportunistic orphan cleanup (fail-open).
    with contextlib.suppress(OSError):
        purge_orphans(workspace)

    if _is_session_end(event):
        with contextlib.suppress(OSError):
            delete_session(workspace, session_id)
        return None

    if _is_stop_event(event, runtime) or event.lower() == "stop":
        result = evaluate_stop(
            workspace=workspace,
            session_id=session_id,
            data=data,
            roots=roots,
        )
        if result is None:
            return None
        message, _hits = result
        try:
            mark_consumed(session_dir(workspace, session_id))
        except OSError:
            return None
        return json.dumps(emit_stop_payload(runtime, message))

    # Tool accumulate (PostToolUse / failure / default when tool fields present).
    if _is_tool_event(event, runtime) or _has_tool_fields(data):
        try:
            _accumulate_tool_event(
                workspace=workspace,
                session_id=session_id,
                data=data,
                roots=roots,
                event=event,
            )
        except OSError:
            return None
        return None

    return None
