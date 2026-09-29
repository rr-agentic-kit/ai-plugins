"""Dual-runtime hook adapter: deny branch-mutating git writes on protected branches."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .command import UNKNOWN_BLOCKED_SUBCOMMAND, find_blocked_subcommand
from .git_state import is_protected_branch, resolve_branch

ResolveBranchFn = Callable[[Path], str | None]


def parse_hook_payload(raw: str) -> dict[str, Any] | None:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def _extract_command(data: dict[str, Any]) -> str | None:
    command = data.get("command")
    if command:
        return str(command)
    tool_input = data.get("tool_input") or data.get("toolInput") or {}
    if isinstance(tool_input, dict):
        nested = tool_input.get("command")
        if nested:
            return str(nested)
    return None


def _extract_cwd(data: dict[str, Any]) -> str | None:
    cwd = data.get("cwd")
    return str(cwd) if cwd else None


def build_block_message(branch: str, subcommand: str) -> str:
    op = (
        "a git write operation (commit/merge/rebase/cherry-pick/revert/reset/am/pull)"
        if subcommand == UNKNOWN_BLOCKED_SUBCOMMAND
        else f"`git {subcommand}`"
    )
    return (
        f'Blocked: {op} on protected branch "{branch}" is not allowed in this '
        "repo. The only writable git action allowed directly on master/main is "
        "`git tag` — everything else (commits, merges, rebases, ...) must land "
        'via PR or a human doing it manually (see AGENTS.md -> "Release-target '
        'PRs"). Create/switch to a feature or release branch instead (e.g. '
        "`git switch -c feat/your-change`) and open a PR against the active "
        "release branch."
    )


def emit_deny_payload(runtime: str, message: str) -> dict[str, Any]:
    if runtime == "claude":
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": message,
            }
        }
    return {"permission": "deny", "user_message": message, "agent_message": message}


def run_hook(
    *,
    runtime: str,
    stdin_text: str,
    resolve_branch_fn: ResolveBranchFn | None = None,
) -> str | None:
    """Return deny JSON string, or None to allow silently.

    Fails open (allow) only on infra errors: bad JSON, non-Bash tool, no
    command, no cwd, or branch resolution failure. A detected blocked write
    (commit/merge/rebase/cherry-pick/revert/reset/am/pull) on a protected
    branch always returns a deny payload; `git tag` is never blocked.
    """
    if runtime not in ("cursor", "claude"):
        return None
    data = parse_hook_payload(stdin_text)
    if data is None:
        return None

    tool_name = data.get("tool_name") or data.get("toolName")
    if runtime == "claude" and tool_name not in (None, "Bash"):
        return None

    command = _extract_command(data)
    if not command:
        return None
    subcommand = find_blocked_subcommand(command)
    if subcommand is None:
        return None

    cwd = _extract_cwd(data)
    if not cwd:
        return None

    branch_fn = resolve_branch_fn or resolve_branch
    branch = branch_fn(Path(cwd))
    if branch is None:
        return None
    if not is_protected_branch(branch):
        return None

    message = build_block_message(branch, subcommand)
    return json.dumps(emit_deny_payload(runtime, message))
