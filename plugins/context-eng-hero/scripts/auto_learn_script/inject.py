"""Emit runtime-correct Stop inject JSON for auto-learn."""

from __future__ import annotations

from typing import Any

from .constants import MESSAGE_CAP
from .score import SignalHit


def build_inject_message(
    *,
    bound_skill: str,
    absorb_into: str,
    signals: list[SignalHit],
) -> str:
    lines = [
        "Run /recipe-context-engineer --auto-learn on "
        f"{absorb_into} using this session as the miss source. "
        "No AskQuestion. Absorb selected skill_gaps.",
        f"bound_skill={bound_skill}",
        f"absorb_into={absorb_into}",
        "signals:",
    ]
    for hit in signals[:5]:
        flag = " [extreme]" if hit.extreme else ""
        lines.append(f"- {hit.class_id}{flag}: {hit.evidence}")
    message = "\n".join(lines)
    if len(message) > MESSAGE_CAP:
        message = message[: MESSAGE_CAP - 20] + "\n…(truncated)"
    return message


def emit_stop_payload(runtime: str, message: str) -> dict[str, Any]:
    """
    Cursor: followup_message (auto-submits next turn).
    Claude: decision block + reason (keeps conversation; additionalContext alone
    can be soft — lock block+reason in tests).
    """
    if runtime == "cursor":
        return {"followup_message": message}
    return {
        "decision": "block",
        "reason": message,
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": message,
        },
    }


def emit_cleanup_payload(runtime: str) -> dict[str, Any] | None:
    """SessionEnd: no inject — empty/silent."""
    del runtime  # parity stub; hosts ignore SessionEnd response.
    return None
