"""Unit tests for context_budget_script.hook (in-process; one shell smoke)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
from context_budget_script.hook import (
    attention_message,
    emit_payload,
    parse_hook_payload,
    resolve_action,
    run_hook,
)
from context_budget_script.tokenize import count_tokens

REPO = Path(__file__).resolve().parents[3]
HOOK = REPO / "plugins" / "rrraw" / "hooks" / "context_budget_hook.sh"
SOFT = 5_000


def _pad_to_tokens(min_tokens: int) -> str:
    chunk = "word " * 50
    text = chunk
    while count_tokens(text) < min_tokens:
        text += chunk
    return text


def _soft_report(path: Path) -> list[dict[str, Any]]:
    return [{"path": str(path), "tokens": SOFT + 10, "tier": "soft"}]


def _ok_report(path: Path) -> list[dict[str, Any]]:
    return [{"path": str(path), "tokens": 100, "tier": "ok"}]


@pytest.fixture()
def soft_plan_file(tmp_path: Path) -> Path:
    plan = tmp_path / "docs" / "rr" / "0.1" / "plan"
    plan.mkdir(parents=True)
    path = plan / "constitution.md"
    path.write_text(_pad_to_tokens(SOFT), encoding="utf-8")
    return path


def test_parse_hook_payload_bad_json() -> None:
    assert parse_hook_payload("not-json") is None
    assert run_hook(runtime="cursor", stdin_text="not-json") is None


def test_under_budget_file_silent(tmp_path: Path) -> None:
    plan = tmp_path / "docs" / "rr" / "0.1" / "plan"
    plan.mkdir(parents=True)
    path = plan / "constitution.md"
    path.write_text("short\n", encoding="utf-8")
    out = run_hook(
        runtime="cursor",
        stdin_text=json.dumps({"file_path": str(path)}),
        measure_file_fn=_ok_report,
    )
    assert out is None


def test_soft_file_cursor_emit(soft_plan_file: Path) -> None:
    raw = run_hook(
        runtime="cursor",
        stdin_text=json.dumps(
            {"file_path": str(soft_plan_file), "hook_event_name": "afterFileEdit"}
        ),
        measure_file_fn=_soft_report,
    )
    assert raw is not None
    out = json.loads(raw)
    assert "additional_context" in out
    assert "agent_message" in out
    assert "soft" in out["additional_context"]
    assert "constitution.md" in out["additional_context"]
    assert "word word word" not in out["additional_context"]


def test_soft_file_claude_emit(soft_plan_file: Path) -> None:
    raw = run_hook(
        runtime="claude",
        stdin_text=json.dumps(
            {
                "tool_input": {"file_path": str(soft_plan_file)},
                "hook_event_name": "PostToolUse",
            }
        ),
        measure_file_fn=_soft_report,
    )
    assert raw is not None
    out = json.loads(raw)
    hso = out["hookSpecificOutput"]
    assert hso["hookEventName"] == "PostToolUse"
    assert "additionalContext" in hso
    assert "soft" in hso["additionalContext"]
    assert "word word word" not in hso["additionalContext"]


def test_prompt_without_rr_planner_silent(tmp_path: Path) -> None:
    plan = tmp_path / "docs" / "rr" / "0.1" / "plan"
    plan.mkdir(parents=True)
    (plan / "constitution.md").write_text(_pad_to_tokens(SOFT), encoding="utf-8")
    out = run_hook(
        runtime="cursor",
        stdin_text=json.dumps(
            {
                "prompt": "please refactor the auth module",
                "cwd": str(tmp_path),
                "workspace_roots": [str(tmp_path)],
            }
        ),
        measure_plan_dir_fn=lambda _p: _soft_report(plan / "constitution.md"),
    )
    assert out is None


def test_prompt_with_rr_planner_resolves_plan_dir(tmp_path: Path) -> None:
    plan = tmp_path / "docs" / "rr" / "0.1" / "plan"
    plan.mkdir(parents=True)
    (plan / "constitution.md").write_text("x\n", encoding="utf-8")
    seen: list[Path] = []

    def capture(path: Path) -> list[dict[str, Any]]:
        seen.append(path)
        return _soft_report(path / "constitution.md")

    action = resolve_action(
        {
            "prompt": "run rr-planner standing",
            "cwd": str(tmp_path),
            "workspace_roots": [str(tmp_path)],
        }
    )
    assert action is not None
    assert action.path.resolve() == plan.resolve()

    raw = run_hook(
        runtime="cursor",
        stdin_text=json.dumps(
            {
                "prompt": "run /rr-planner --optimize",
                "cwd": str(tmp_path),
                "workspace_roots": [str(tmp_path)],
            }
        ),
        measure_plan_dir_fn=capture,
    )
    assert raw is not None
    assert seen and seen[0].resolve() == plan.resolve()
    assert "soft" in json.loads(raw)["additional_context"]


def test_attention_message_skips_ok() -> None:
    assert attention_message([{"path": "a.md", "tokens": 1, "tier": "ok"}]) is None
    msg = attention_message(
        [{"path": "a.md", "tokens": 6000, "tier": "soft", "body": "SECRET"}]
    )
    assert msg is not None
    assert "SECRET" not in msg
    assert "6000" in msg


def test_emit_payload_shapes() -> None:
    cursor = emit_payload("cursor", "hello")
    assert cursor == {"additional_context": "hello", "agent_message": "hello"}
    claude = emit_payload("claude", "hello", hook_event="UserPromptSubmit")
    assert claude["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert claude["hookSpecificOutput"]["additionalContext"] == "hello"


def test_shell_fail_open_bad_json() -> None:
    """Thin launcher smoke: bad JSON still exit 0."""
    proc = subprocess.run(
        ["sh", str(HOOK), "--runtime", "cursor"],
        input="not-json",
        capture_output=True,
        text=True,
        cwd=str(REPO / "plugins" / "rrraw"),
        check=False,
        timeout=30,
    )
    assert proc.returncode == 0
    assert proc.stdout.strip() == ""
