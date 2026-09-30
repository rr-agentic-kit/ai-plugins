"""Unit tests for auto_learn_script (gates, score, inject, reentry)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from auto_learn_script.accumulate import accumulate, maybe_bind_skill
from auto_learn_script.gates import is_cache_path, is_local_source_skill
from auto_learn_script.hook import evaluate_stop, parse_hook_payload, run_hook
from auto_learn_script.inject import build_inject_message, emit_stop_payload
from auto_learn_script.score import (
    meets_inject_bar,
    score_events,
    score_reread,
    score_tool_fail_retry,
    score_tool_thrash,
)
from auto_learn_script.store import load_state, mark_consumed, session_dir

REPO = Path(__file__).resolve().parents[3]
HOOK = REPO / "plugins" / "context-eng-hero" / "hooks" / "auto_learn_hook.sh"


def _skill_path(tmp: Path, name: str = "demo-skill") -> Path:
    path = tmp / "plugins" / "demo" / "skills" / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Demo\n", encoding="utf-8")
    return path


def _read_event(path: Path, *, failed: bool = False) -> dict:
    return {
        "tool_name": "Read",
        "tool_input": {"file_path": str(path)},
        "failed": failed,
    }


def test_parse_hook_payload_bad_json() -> None:
    assert parse_hook_payload("not-json") is None
    assert run_hook(runtime="cursor", stdin_text="not-json") is None


def test_cache_path_rejected(tmp_path: Path) -> None:
    cache = (
        Path.home()
        / ".claude"
        / "plugins"
        / "cache"
        / "ai-plugins"
        / "context-eng-hero"
        / "0.0.1"
        / "skills"
        / "x"
        / "SKILL.md"
    )
    assert is_cache_path(cache)
    assert not is_local_source_skill(cache, [str(tmp_path)])


def test_local_skill_under_workspace(tmp_path: Path) -> None:
    skill = _skill_path(tmp_path)
    assert is_local_source_skill(skill, [str(tmp_path)])
    outside = Path("/tmp/other/plugins/x/skills/y/SKILL.md")
    assert not is_local_source_skill(outside, [str(tmp_path)])


def test_cursor_cache_rejected(tmp_path: Path) -> None:
    cache = (
        Path.home()
        / ".cursor"
        / "plugins"
        / "cache"
        / "ctx"
        / "skills"
        / "x"
        / "SKILL.md"
    )
    assert is_cache_path(cache)
    assert not is_local_source_skill(cache, [str(Path.home())])


def test_thrash_and_reread_meet_bar(tmp_path: Path) -> None:
    skill = _skill_path(tmp_path)
    events = [
        {"tool": "Read", "fingerprint": str(skill), "path": str(skill)},
        *[{"tool": "Grep", "fingerprint": f"q{i}"} for i in range(6)],
        {"tool": "Read", "fingerprint": str(skill), "path": str(skill)},
        {"tool": "Read", "fingerprint": str(skill), "path": str(skill)},
    ]
    hits = score_events(events, skill_bound=True)
    ids = {h.class_id for h in hits}
    assert "tool_thrash" in ids or "reread" in ids
    # Force both classes present for bar.
    thrash = score_tool_thrash([{"tool": "Read", "fingerprint": "a"}] * 8)
    reread = score_reread(
        [{"tool": "Read", "fingerprint": str(skill), "path": str(skill)}] * 3
    )
    assert thrash is not None and reread is not None
    assert meets_inject_bar([thrash, reread])


def test_below_threshold_silence() -> None:
    events = [
        {"tool": "Read", "fingerprint": "/x"},
        {"tool": "Write", "fingerprint": "/y"},
        {"tool": "Read", "fingerprint": "/x"},
    ]
    hits = score_events(events, skill_bound=True)
    assert not meets_inject_bar(hits)


def test_extreme_reread_alone_meets_bar() -> None:
    path = "/ws/plugins/a/skills/b/SKILL.md"
    events = [{"tool": "Read", "fingerprint": path, "path": path}] * 6
    hit = score_reread(events)
    assert hit is not None and hit.extreme
    assert meets_inject_bar([hit])


def test_fail_retry_signal() -> None:
    events = [
        {"tool": "Bash", "fingerprint": "rg foo", "failed": True},
        {"tool": "Bash", "fingerprint": "rg foo", "failed": False},
    ]
    hit = score_tool_fail_retry(events)
    assert hit is not None
    assert hit.class_id == "tool_fail_retry"


def test_accumulate_binds_local_skill(tmp_path: Path) -> None:
    skill = _skill_path(tmp_path)
    ok = accumulate(
        workspace=tmp_path,
        session_id="s1",
        data={
            "tool_name": "Read",
            "tool_input": {"file_path": str(skill)},
            "hook_event_name": "postToolUse",
        },
        roots=[str(tmp_path)],
    )
    assert ok
    state = load_state(session_dir(tmp_path, "s1"))
    assert state["bound_skill"] == str(skill)
    assert state["absorb_into"] == str(skill)


def test_accumulate_ignores_cache_skill(tmp_path: Path) -> None:
    cache = (
        Path.home()
        / ".claude"
        / "plugins"
        / "cache"
        / "ai-plugins"
        / "x"
        / "skills"
        / "y"
        / "SKILL.md"
    )
    state = maybe_bind_skill({}, str(cache), [str(Path.home())])
    assert state.get("bound_skill") is None


def test_stop_inject_cursor_and_claude(tmp_path: Path) -> None:
    skill = _skill_path(tmp_path)
    session_id = "inj1"
    # Bind + thrash + reread evidence.
    accumulate(
        workspace=tmp_path,
        session_id=session_id,
        data=_read_event(skill),
        roots=[str(tmp_path)],
    )
    for i in range(6):
        accumulate(
            workspace=tmp_path,
            session_id=session_id,
            data={
                "tool_name": "Grep",
                "tool_input": {"pattern": f"p{i}", "path": str(tmp_path)},
            },
            roots=[str(tmp_path)],
        )
    for _ in range(2):
        accumulate(
            workspace=tmp_path,
            session_id=session_id,
            data=_read_event(skill),
            roots=[str(tmp_path)],
        )

    stop_payload = {
        "hook_event_name": "stop",
        "session_id": session_id,
        "cwd": str(tmp_path),
        "workspace_roots": [str(tmp_path)],
    }
    out_c = run_hook(runtime="cursor", stdin_text=json.dumps(stop_payload))
    assert out_c is not None
    cursor = json.loads(out_c)
    assert "followup_message" in cursor
    assert "--auto-learn" in cursor["followup_message"]
    assert str(skill) in cursor["followup_message"]

    # Consumed → second stop silent.
    out2 = run_hook(runtime="cursor", stdin_text=json.dumps(stop_payload))
    assert out2 is None

    # Fresh session for Claude shape.
    session_id2 = "inj2"
    accumulate(
        workspace=tmp_path,
        session_id=session_id2,
        data=_read_event(skill),
        roots=[str(tmp_path)],
    )
    for i in range(6):
        accumulate(
            workspace=tmp_path,
            session_id=session_id2,
            data={
                "tool_name": "Grep",
                "tool_input": {"pattern": f"q{i}", "path": str(tmp_path)},
            },
            roots=[str(tmp_path)],
        )
    for _ in range(2):
        accumulate(
            workspace=tmp_path,
            session_id=session_id2,
            data=_read_event(skill),
            roots=[str(tmp_path)],
        )
    stop2 = {
        "hook_event_name": "Stop",
        "session_id": session_id2,
        "cwd": str(tmp_path),
        "workspace_roots": [str(tmp_path)],
    }
    out_cl = run_hook(runtime="claude", stdin_text=json.dumps(stop2))
    assert out_cl is not None
    claude = json.loads(out_cl)
    assert claude["decision"] == "block"
    assert "--auto-learn" in claude["reason"]
    assert claude["hookSpecificOutput"]["hookEventName"] == "Stop"


def test_reentry_stop_hook_active(tmp_path: Path) -> None:
    skill = _skill_path(tmp_path)
    session_id = "re1"
    accumulate(
        workspace=tmp_path,
        session_id=session_id,
        data=_read_event(skill),
        roots=[str(tmp_path)],
    )
    for i in range(8):
        accumulate(
            workspace=tmp_path,
            session_id=session_id,
            data={"tool_name": "Glob", "tool_input": {"pattern": f"*{i}"}},
            roots=[str(tmp_path)],
        )
    for _ in range(3):
        accumulate(
            workspace=tmp_path,
            session_id=session_id,
            data=_read_event(skill),
            roots=[str(tmp_path)],
        )
    payload = {
        "hook_event_name": "stop",
        "session_id": session_id,
        "cwd": str(tmp_path),
        "workspace_roots": [str(tmp_path)],
        "stop_hook_active": True,
    }
    assert run_hook(runtime="cursor", stdin_text=json.dumps(payload)) is None


def test_emit_payload_shapes() -> None:
    msg = build_inject_message(
        bound_skill="/ws/plugins/a/skills/b/SKILL.md",
        absorb_into="/ws/plugins/a/skills/b/SKILL.md",
        signals=[],
    )
    assert emit_stop_payload("cursor", msg) == {"followup_message": msg}
    claude = emit_stop_payload("claude", msg)
    assert claude["decision"] == "block"
    assert claude["reason"] == msg


def test_session_end_cleanup(tmp_path: Path) -> None:
    skill = _skill_path(tmp_path)
    session_id = "end1"
    accumulate(
        workspace=tmp_path,
        session_id=session_id,
        data=_read_event(skill),
        roots=[str(tmp_path)],
    )
    assert session_dir(tmp_path, session_id).is_dir()
    run_hook(
        runtime="cursor",
        stdin_text=json.dumps(
            {
                "hook_event_name": "sessionEnd",
                "session_id": session_id,
                "cwd": str(tmp_path),
            }
        ),
    )
    assert not session_dir(tmp_path, session_id).is_dir()


def test_mark_consumed_blocks_evaluate(tmp_path: Path) -> None:
    skill = _skill_path(tmp_path)
    session_id = "c1"
    accumulate(
        workspace=tmp_path,
        session_id=session_id,
        data=_read_event(skill),
        roots=[str(tmp_path)],
    )
    for i in range(8):
        accumulate(
            workspace=tmp_path,
            session_id=session_id,
            data={"tool_name": "Bash", "tool_input": {"command": f"ls {i}"}},
            roots=[str(tmp_path)],
        )
    for _ in range(3):
        accumulate(
            workspace=tmp_path,
            session_id=session_id,
            data=_read_event(skill),
            roots=[str(tmp_path)],
        )
    mark_consumed(session_dir(tmp_path, session_id))
    result = evaluate_stop(
        workspace=tmp_path,
        session_id=session_id,
        data={},
        roots=[str(tmp_path)],
    )
    assert result is None


@pytest.mark.skipif(not HOOK.is_file(), reason="hook script missing")
def test_hook_shell_fail_open() -> None:
    proc = subprocess.run(
        [str(HOOK), "--runtime", "cursor"],
        input=b"not-json",
        capture_output=True,
        check=False,
        timeout=30,
    )
    assert proc.returncode == 0
    assert proc.stdout == b""
