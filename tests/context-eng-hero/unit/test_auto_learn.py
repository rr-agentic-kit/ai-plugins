"""Unit tests for auto_learn_script (gates, score, inject, reentry)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from auto_learn_script.accumulate import accumulate, maybe_bind_skill
from auto_learn_script.cli import require_python, run_hook_mode
from auto_learn_script.constants import BASH_INFO_MIN, ORPHAN_TTL_DAYS, THRASH_MIN
from auto_learn_script.gates import (
    default_workspace_roots,
    is_cache_path,
    is_local_source_skill,
    looks_like_skill_md,
    under_roots,
)
from auto_learn_script.hook import evaluate_stop, parse_hook_payload, run_hook
from auto_learn_script.inject import build_inject_message, emit_stop_payload
from auto_learn_script.score import (
    meets_inject_bar,
    score_bash_info_loop,
    score_correction,
    score_events,
    score_reread,
    score_tool_fail_retry,
    score_tool_thrash,
)
from auto_learn_script.store import (
    load_events,
    load_state,
    mark_consumed,
    purge_orphans,
    session_dir,
)

REPO = Path(__file__).resolve().parents[3]
HOOK = REPO / "plugins" / "context-eng-hero" / "hooks" / "auto_learn_hook.sh"
LAUNCHER = REPO / "plugins" / "context-eng-hero" / "scripts" / "auto_learn.sh"


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
    assert "tool_thrash" in ids
    assert "reread" in ids
    assert meets_inject_bar(hits)


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
    assert not meets_inject_bar([hit])
    path = "/ws/plugins/a/skills/b/SKILL.md"
    reread = score_reread([{"tool": "Read", "fingerprint": path, "path": path}] * 3)
    assert reread is not None
    assert meets_inject_bar([hit, reread])


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


def test_default_workspace_roots_env_and_dedupe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("CURSOR_PROJECT_DIR", raising=False)
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    # Empty → cwd.
    roots = default_workspace_roots()
    assert roots == [str(tmp_path)] or any(
        Path(r).resolve() == tmp_path.resolve() for r in roots
    )
    # Payload + cwd + env, with dedupe.
    env_root = tmp_path / "from-env"
    env_root.mkdir()
    monkeypatch.setenv("CURSOR_PROJECT_DIR", str(env_root))
    payload = [str(tmp_path), str(tmp_path)]
    roots = default_workspace_roots(payload, cwd=str(tmp_path))
    resolved = {Path(r).resolve() for r in roots}
    assert tmp_path.resolve() in resolved
    assert env_root.resolve() in resolved
    assert len(roots) == len(resolved)
    monkeypatch.delenv("CURSOR_PROJECT_DIR")
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(env_root))
    roots_claude = default_workspace_roots(cwd=str(tmp_path))
    assert env_root.resolve() in {Path(r).resolve() for r in roots_claude}


@pytest.mark.parametrize(
    "rel",
    [
        "plugins/demo/skills/x/SKILL.md",
        ".claude/skills/x/SKILL.md",
        ".agents/skills/x/SKILL.md",
        "skills/x/SKILL.md",
    ],
)
def test_looks_like_skill_md_arms(tmp_path: Path, rel: str) -> None:
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# x\n", encoding="utf-8")
    assert looks_like_skill_md(path)
    assert looks_like_skill_md(str(path))
    assert not looks_like_skill_md(tmp_path / "README.md")


def test_under_roots_branches(tmp_path: Path) -> None:
    child = tmp_path / "a" / "b.py"
    child.parent.mkdir(parents=True)
    child.write_text("x", encoding="utf-8")
    assert under_roots(child, [str(tmp_path)])
    assert under_roots(tmp_path, [str(tmp_path)])
    assert not under_roots(tmp_path / "nope", [str(tmp_path / "other")])
    assert not under_roots(child, [])


def test_score_bash_info_loop() -> None:
    assert score_bash_info_loop([], skill_bound=False) is None
    events = [
        {"tool": "Bash", "fingerprint": "rg pattern", "cmd": "rg pattern"}
        for _ in range(BASH_INFO_MIN)
    ]
    assert score_bash_info_loop(events, skill_bound=False) is None
    hit = score_bash_info_loop(events, skill_bound=True)
    assert hit is not None
    assert hit.class_id == "bash_info_loop"
    under = events[: BASH_INFO_MIN - 1]
    assert score_bash_info_loop(under, skill_bound=True) is None


def test_score_correction_with_thrash() -> None:
    thrash_events = [
        {"tool": "Grep", "fingerprint": f"q{i}"} for i in range(THRASH_MIN)
    ]
    hit = score_correction(thrash_events, "that is wrong — fix this")
    assert hit is not None
    assert hit.class_id == "correction"
    assert score_correction(thrash_events, "please continue") is None
    soft = [{"tool": "Read", "fingerprint": f"p{i}"} for i in range(3)]
    soft_hit = score_correction(soft, "don't do that")
    assert soft_hit is not None


def test_thrash_write_resets_streak() -> None:
    events = [
        *[{"tool": "Grep", "fingerprint": f"a{i}"} for i in range(4)],
        {"tool": "Write", "fingerprint": "/out"},
        *[{"tool": "Grep", "fingerprint": f"b{i}"} for i in range(4)],
    ]
    assert score_tool_thrash(events) is None
    long = [{"tool": "Grep", "fingerprint": f"c{i}"} for i in range(THRASH_MIN)]
    assert score_tool_thrash(long) is not None


def test_purge_orphans_ttl(tmp_path: Path) -> None:
    import os
    import time

    old = session_dir(tmp_path, "old")
    new = session_dir(tmp_path, "new")
    old.mkdir(parents=True)
    new.mkdir(parents=True)
    stale = time.time() - (ORPHAN_TTL_DAYS + 1) * 86400
    os.utime(old, (stale, stale))
    removed = purge_orphans(tmp_path, ttl_days=ORPHAN_TTL_DAYS)
    assert removed == 1
    assert not old.is_dir()
    assert new.is_dir()


def test_load_state_corrupt_fail_open(tmp_path: Path) -> None:
    session = session_dir(tmp_path, "bad")
    session.mkdir(parents=True)
    (session / "state.json").write_text("not-json", encoding="utf-8")
    state = load_state(session)
    assert state["bound_skill"] is None
    assert state["consumed"] is False
    (session / "state.json").write_text("[]\n", encoding="utf-8")
    state2 = load_state(session)
    assert isinstance(state2, dict)
    assert state2["bound_skill"] is None


def test_cli_hook_fail_open(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(**_kwargs: object) -> str | None:
        raise RuntimeError("boom")

    monkeypatch.setattr("auto_learn_script.hook.run_hook", boom)
    monkeypatch.setattr("sys.stdin", type("S", (), {"read": lambda self: "{}"})())
    assert run_hook_mode("cursor") == 0


def test_require_python_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "auto_learn_script.cli.sys.version_info",
        (3, 13, 0),
    )
    with pytest.raises(SystemExit) as exc:
        require_python()
    assert exc.value.code == 127


@pytest.mark.skipif(not LAUNCHER.is_file(), reason="launcher missing")
def test_auto_learn_sh_hook_no_python_exit_0(tmp_path: Path) -> None:
    # Isolate from monorepo .venv / uv discovery: copy launcher only (no package).
    isolated = tmp_path / "scripts"
    isolated.mkdir()
    dest = isolated / "auto_learn.sh"
    dest.write_text(LAUNCHER.read_text(encoding="utf-8"), encoding="utf-8")
    dest.chmod(0o755)
    env = {
        "PATH": str(tmp_path / "empty-bin"),
        "HOME": str(tmp_path),
    }
    (tmp_path / "empty-bin").mkdir()
    proc = subprocess.run(
        [str(dest), "--hook", "--runtime", "cursor"],
        input=b"{}",
        capture_output=True,
        check=False,
        timeout=30,
        env=env,
        cwd=str(tmp_path),
    )
    assert proc.returncode == 0


@pytest.mark.skipif(not HOOK.is_file(), reason="hook script missing")
def test_hook_shell_invalid_runtime_exit_0() -> None:
    proc = subprocess.run(
        [str(HOOK), "--runtime", "nope"],
        input=b"{}",
        capture_output=True,
        check=False,
        timeout=30,
    )
    assert proc.returncode == 0
    assert proc.stdout == b""


def test_reentry_loop_count_blocks(tmp_path: Path) -> None:
    skill = _skill_path(tmp_path)
    session_id = "loop1"
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
        "loop_count": 1,
    }
    assert run_hook(runtime="cursor", stdin_text=json.dumps(payload)) is None


def test_accumulate_camel_case_claude_fields(tmp_path: Path) -> None:
    skill = _skill_path(tmp_path)
    ok = accumulate(
        workspace=tmp_path,
        session_id="camel1",
        data={
            "toolName": "Read",
            "toolInput": {"filePath": str(skill)},
            "hookEventName": "postToolUse",
        },
        roots=[str(tmp_path)],
    )
    assert ok
    state = load_state(session_dir(tmp_path, "camel1"))
    assert state["bound_skill"] == str(skill)
    events = load_events(session_dir(tmp_path, "camel1"))
    assert events and events[0]["tool"] == "Read"


def test_post_tool_use_failure_via_run_hook(tmp_path: Path) -> None:
    payload = {
        "hook_event_name": "postToolUseFailure",
        "session_id": "fail1",
        "cwd": str(tmp_path),
        "workspace_roots": [str(tmp_path)],
        "tool_name": "Bash",
        "tool_input": {"command": "rg missing"},
        "failed": True,
    }
    assert run_hook(runtime="cursor", stdin_text=json.dumps(payload)) is None
    events = load_events(session_dir(tmp_path, "fail1"))
    assert events
    assert events[0]["failed"] is True


def test_redact_secrets_common_shapes() -> None:
    from auto_learn_script.redact import redact_secrets
    from auto_learn_script.score import fingerprint_cmd

    bearer = 'curl -H "Authorization: Bearer supersecrettoken"'
    scrubbed = redact_secrets(bearer)
    assert "supersecrettoken" not in scrubbed
    assert "[REDACTED]" in scrubbed

    assert "sk-abcdefghijklmnopqrstuvwxyz" not in redact_secrets(
        "key sk-abcdefghijklmnopqrstuvwxyz end"
    )
    assert "ghp_abcdefghijklmnopqrstuv" not in redact_secrets(
        "auth ghp_abcdefghijklmnopqrstuv"
    )
    fp = fingerprint_cmd("curl -H 'Authorization: Bearer abcdefghijklmnop'")
    assert "abcdefghijklmnop" not in fp
    assert "[REDACTED]" in fp


def test_accumulate_redacts_user_text_and_cmd(tmp_path: Path) -> None:
    ok = accumulate(
        workspace=tmp_path,
        session_id="sec1",
        data={
            "tool_name": "Bash",
            "tool_input": {
                "command": "curl -H 'Authorization: Bearer leakytoken123' https://x"
            },
        },
        roots=[str(tmp_path)],
        user_text="wrong — use api_key=supersecretvalue instead",
    )
    assert ok
    session = session_dir(tmp_path, "sec1")
    state = load_state(session)
    assert "supersecretvalue" not in (state.get("last_user_text") or "")
    assert "[REDACTED]" in (state.get("last_user_text") or "")
    events = load_events(session)
    assert events
    assert "leakytoken123" not in json.dumps(events[0])
    assert "[REDACTED]" in (events[0].get("cmd") or "")


def test_accumulate_truncates_user_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("auto_learn_script.accumulate.MAX_USER_TEXT", 40)
    ok = accumulate(
        workspace=tmp_path,
        session_id="cap1",
        data={"tool_name": "Grep", "tool_input": {"pattern": "x"}},
        roots=[str(tmp_path)],
        user_text="x" * 200,
    )
    assert ok
    text = load_state(session_dir(tmp_path, "cap1"))["last_user_text"]
    assert text is not None
    assert len(text) <= 40
    assert text.endswith("…(truncated)")


def test_append_event_caps_count(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from auto_learn_script.store import append_event, ensure_session

    monkeypatch.setattr("auto_learn_script.store.MAX_EVENTS", 5)
    monkeypatch.setattr("auto_learn_script.store.MAX_EVENTS_BYTES", 50_000)
    session = ensure_session(tmp_path, "cap-events")
    assert session is not None
    for i in range(12):
        assert append_event(session, {"tool": "Grep", "fingerprint": f"q{i}", "n": i})
    events = load_events(session)
    assert len(events) == 5
    assert events[0]["n"] == 7
    assert events[-1]["n"] == 11


def test_inject_message_redacts_evidence() -> None:
    from auto_learn_script.score import SignalHit

    msg = build_inject_message(
        bound_skill="/ws/plugins/a/skills/b/SKILL.md",
        absorb_into="/ws/plugins/a/skills/b/SKILL.md",
        signals=[
            SignalHit(
                "bash_info_loop",
                "3 discovery Bash (curl -H Authorization: Bearer tok123456)",
            )
        ],
    )
    assert "tok123456" not in msg
    assert "[REDACTED]" in msg
