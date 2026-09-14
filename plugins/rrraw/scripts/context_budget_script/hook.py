"""Dual-runtime hook adapter: filter host JSON → measure → inject receipts."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .constants import is_plan_markdown

MeasureFileFn = Callable[[Path], list[dict[str, Any]]]
MeasurePlanDirFn = Callable[[Path], list[dict[str, Any]]]

_MESSAGE_CAP = 10_000
_PLANNER_RE = re.compile(r"rr-planner|/rr-planner", re.I)


@dataclass(frozen=True)
class FileAction:
    path: Path


@dataclass(frozen=True)
class PlanDirAction:
    path: Path


Action = FileAction | PlanDirAction


def parse_hook_payload(raw: str) -> dict[str, Any] | None:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def prompt_mentions_planner(prompt: str) -> bool:
    return bool(_PLANNER_RE.search(prompt or ""))


def find_plan_dir(start: Path) -> Path | None:
    cur = start if start.is_dir() else start.parent
    for _ in range(8):
        norm = cur.as_posix().replace("\\", "/").lower()
        if cur.name == "plan" and (
            (cur.parent / "discovery").exists() or "/docs/rr/" in norm
        ):
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    cur = start if start.is_dir() else start.parent
    for _ in range(12):
        candidate = cur / "docs" / "rr"
        if candidate.is_dir():
            for track in sorted(candidate.iterdir()):
                plan = track / "plan"
                if plan.is_dir():
                    return plan
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def _extract_file_path(data: dict[str, Any]) -> str | None:
    file_path = data.get("file_path") or data.get("filePath")
    if file_path:
        return str(file_path)
    tool_input = data.get("tool_input") or data.get("toolInput") or {}
    if isinstance(tool_input, dict):
        nested = tool_input.get("file_path") or tool_input.get("filePath")
        if nested:
            return str(nested)
    return None


def _extract_prompt(data: dict[str, Any]) -> str:
    prompt = (
        data.get("prompt") or data.get("user_prompt") or data.get("userPrompt") or ""
    )
    return str(prompt) if prompt else ""


def _workspace_roots(data: dict[str, Any]) -> list[str]:
    roots = data.get("workspace_roots") or data.get("cwd") or []
    if isinstance(roots, str):
        roots = [roots]
    if not roots:
        cwd = data.get("cwd")
        if cwd:
            roots = [cwd]
    return [str(r) for r in roots]


def resolve_action(data: dict[str, Any]) -> Action | None:
    file_path = _extract_file_path(data)
    if file_path and is_plan_markdown(Path(file_path)):
        return FileAction(path=Path(file_path))

    prompt = _extract_prompt(data)
    if not prompt or not prompt_mentions_planner(prompt):
        return None

    plan: Path | None = None
    for root in _workspace_roots(data):
        plan = find_plan_dir(Path(root))
        if plan is not None:
            break
    if plan is None:
        plan = find_plan_dir(Path.cwd())
    if plan is None:
        return None
    return PlanDirAction(path=plan)


def attention_message(files: list[dict[str, Any]]) -> str | None:
    lines: list[str] = []
    for f in files:
        tier = f.get("tier")
        if tier not in ("soft", "hard"):
            continue
        path = f.get("path", "?")
        tokens = f.get("tokens", "?")
        lines.append(
            f"- {path}: {tokens} tokens ({tier}) — needs attention; "
            "consider rr-planner --optimize"
        )
    if not lines:
        return None
    header = (
        "rrraw context budget: plan doc(s) need attention "
        "(tiktoken cl100k_base; soft≥5k hard≥8k):"
    )
    return header + "\n" + "\n".join(lines)


def emit_payload(
    runtime: str,
    message: str,
    hook_event: str | None = None,
) -> dict[str, Any]:
    if len(message) > _MESSAGE_CAP:
        message = message[:9900] + "\n…(truncated)"
    if runtime == "claude":
        return {
            "hookSpecificOutput": {
                "hookEventName": hook_event or "PostToolUse",
                "additionalContext": message,
            }
        }
    return {
        "additional_context": message,
        "agent_message": message,
    }


def _default_measure_file(path: Path) -> list[dict[str, Any]]:
    from .cli import measure_file

    result = measure_file(path)
    return result if result is not None else []


def _default_measure_plan_dir(path: Path) -> list[dict[str, Any]]:
    from .cli import measure_plan_dir

    result = measure_plan_dir(path)
    return result if result is not None else []


def run_hook(
    *,
    runtime: str,
    stdin_text: str,
    measure_file_fn: MeasureFileFn | None = None,
    measure_plan_dir_fn: MeasurePlanDirFn | None = None,
) -> str | None:
    """Return inject JSON string, or None for silent (fail-open)."""
    if runtime not in ("cursor", "claude"):
        return None
    data = parse_hook_payload(stdin_text)
    if data is None:
        return None
    action = resolve_action(data)
    if action is None:
        return None

    file_fn = measure_file_fn or _default_measure_file
    plan_fn = measure_plan_dir_fn or _default_measure_plan_dir

    try:
        if isinstance(action, FileAction):
            files = file_fn(action.path)
            hook_event = "PostToolUse" if runtime == "claude" else None
        else:
            files = plan_fn(action.path)
            hook_event = "UserPromptSubmit" if runtime == "claude" else None
    except OSError:
        return None

    message = attention_message(files)
    if message is None:
        return None
    return json.dumps(emit_payload(runtime, message, hook_event=hook_event))
