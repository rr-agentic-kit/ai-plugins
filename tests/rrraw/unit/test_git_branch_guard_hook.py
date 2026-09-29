"""Unit tests for git_branch_guard_script (in-process; one shell smoke)."""

from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

import pytest
from git_branch_guard_script.command import (
    UNKNOWN_BLOCKED_SUBCOMMAND,
    find_blocked_subcommand,
)
from git_branch_guard_script.git_state import is_protected_branch, resolve_branch
from git_branch_guard_script.hook import (
    build_block_message,
    emit_deny_payload,
    parse_hook_payload,
    run_hook,
)

REPO = Path(__file__).resolve().parents[3]
HOOK = REPO / "plugins" / "rrraw" / "hooks" / "git_branch_guard_hook.sh"


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=True)


@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    _run(["git", "init", "-b", "master", "."], tmp_path)
    _run(["git", "config", "user.email", "test@example.com"], tmp_path)
    _run(["git", "config", "user.name", "Test"], tmp_path)
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    _run(["git", "add", "README.md"], tmp_path)
    _run(["git", "commit", "-m", "init"], tmp_path)
    return tmp_path


def test_parse_hook_payload_bad_json() -> None:
    assert parse_hook_payload("not-json") is None
    assert run_hook(runtime="cursor", stdin_text="not-json") is None


def test_find_blocked_subcommand_simple() -> None:
    assert find_blocked_subcommand("git commit -m x") == "commit"
    assert find_blocked_subcommand("git status") is None
    assert find_blocked_subcommand("git commit-tree x") is None


@pytest.mark.parametrize(
    "subcommand",
    ["commit", "merge", "rebase", "cherry-pick", "revert", "reset", "am", "pull"],
)
def test_find_blocked_subcommand_covers_all_write_ops(subcommand: str) -> None:
    assert find_blocked_subcommand(f"git {subcommand} foo") == subcommand


def test_find_blocked_subcommand_allows_tag() -> None:
    assert find_blocked_subcommand("git tag v1.0.0") is None
    assert find_blocked_subcommand("git tag -a v1.0.0 -m release") is None


@pytest.mark.parametrize(
    "command",
    [
        "git add -A && git commit -m x",
        "git commit -m x; echo done",
        'cd repo && git commit -m "wip"',
        "echo msg | git commit -F -",
        "(git commit -m x)",
        "sudo git commit -m x",
        "git -C /tmp/repo commit -m x",
        "git add -A && git merge feat/x",
    ],
)
def test_find_blocked_subcommand_compound(command: str) -> None:
    assert find_blocked_subcommand(command) is not None


def test_find_blocked_subcommand_shell_wrapper() -> None:
    assert find_blocked_subcommand('bash -c "git commit -m x"') == "commit"
    assert find_blocked_subcommand('bash -c "cd x && git merge y"') == "merge"


def test_find_blocked_subcommand_false_positives_avoided() -> None:
    assert find_blocked_subcommand('git log --grep="git commit"') is None
    assert find_blocked_subcommand('echo "please run git commit later"') is None
    assert find_blocked_subcommand("git merge-base a b") is None


def test_find_blocked_subcommand_unparseable_fallback() -> None:
    assert find_blocked_subcommand('git commit -m "oops') == "commit"
    assert find_blocked_subcommand('echo "oops') is None


def test_find_blocked_subcommand_depth_cap_is_conservative() -> None:
    command = "echo hi"
    for _ in range(6):
        command = f"bash -c {shlex.quote(command)}"
    assert find_blocked_subcommand(command) == UNKNOWN_BLOCKED_SUBCOMMAND


def test_resolve_branch_and_protected(git_repo: Path) -> None:
    assert resolve_branch(git_repo) == "master"
    assert is_protected_branch("master") is True
    assert is_protected_branch("main") is True
    assert is_protected_branch("Main") is False
    assert is_protected_branch("feat/x") is False


def test_resolve_branch_not_a_repo(tmp_path: Path) -> None:
    assert resolve_branch(tmp_path) is None


def test_run_hook_claude_blocks_on_master(git_repo: Path) -> None:
    raw = run_hook(
        runtime="claude",
        stdin_text=json.dumps(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "git commit -m x"},
                "cwd": str(git_repo),
            }
        ),
        resolve_branch_fn=lambda _cwd: "master",
    )
    assert raw is not None
    out = json.loads(raw)
    hso = out["hookSpecificOutput"]
    assert hso["hookEventName"] == "PreToolUse"
    assert hso["permissionDecision"] == "deny"
    assert "master" in hso["permissionDecisionReason"]
    assert "AGENTS.md" in hso["permissionDecisionReason"]


def test_run_hook_cursor_blocks_on_main(git_repo: Path) -> None:
    raw = run_hook(
        runtime="cursor",
        stdin_text=json.dumps(
            {"command": "git commit -m x", "cwd": str(git_repo), "sandbox": False}
        ),
        resolve_branch_fn=lambda _cwd: "main",
    )
    assert raw is not None
    out = json.loads(raw)
    assert out["permission"] == "deny"
    assert out["user_message"] == out["agent_message"]
    assert "main" in out["user_message"]


def test_run_hook_allows_feature_branch() -> None:
    for runtime, payload in (
        (
            "claude",
            {"tool_input": {"command": "git commit -m x"}, "cwd": "/repo"},
        ),
        ("cursor", {"command": "git commit -m x", "cwd": "/repo"}),
    ):
        out = run_hook(
            runtime=runtime,
            stdin_text=json.dumps(payload),
            resolve_branch_fn=lambda _cwd: "feat/blocking-master-commit",
        )
        assert out is None


def test_run_hook_allows_non_write_command() -> None:
    def _boom(_cwd: Path) -> str | None:
        raise AssertionError("branch resolution must not run for non-write commands")

    out = run_hook(
        runtime="claude",
        stdin_text=json.dumps(
            {"tool_input": {"command": "git status"}, "cwd": "/repo"}
        ),
        resolve_branch_fn=_boom,
    )
    assert out is None


def test_run_hook_allows_tag_on_master(git_repo: Path) -> None:
    out = run_hook(
        runtime="claude",
        stdin_text=json.dumps(
            {"tool_input": {"command": "git tag v1.0.0"}, "cwd": str(git_repo)}
        ),
        resolve_branch_fn=lambda _cwd: "master",
    )
    assert out is None


def test_run_hook_blocks_merge_on_master(git_repo: Path) -> None:
    raw = run_hook(
        runtime="claude",
        stdin_text=json.dumps(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "git merge feat/x"},
                "cwd": str(git_repo),
            }
        ),
        resolve_branch_fn=lambda _cwd: "master",
    )
    assert raw is not None
    reason = json.loads(raw)["hookSpecificOutput"]["permissionDecisionReason"]
    assert "git merge" in reason


def test_run_hook_fails_open_no_cwd() -> None:
    out = run_hook(
        runtime="claude",
        stdin_text=json.dumps({"tool_input": {"command": "git commit -m x"}}),
    )
    assert out is None


def test_run_hook_fails_open_branch_resolution_error() -> None:
    out = run_hook(
        runtime="claude",
        stdin_text=json.dumps(
            {"tool_input": {"command": "git commit -m x"}, "cwd": "/repo"}
        ),
        resolve_branch_fn=lambda _cwd: None,
    )
    assert out is None


def test_run_hook_ignores_non_bash_tool_claude() -> None:
    out = run_hook(
        runtime="claude",
        stdin_text=json.dumps(
            {
                "tool_name": "Edit",
                "tool_input": {"command": "git commit -m x"},
                "cwd": "/repo",
            }
        ),
        resolve_branch_fn=lambda _cwd: "master",
    )
    assert out is None


def test_build_block_message_names_subcommand() -> None:
    msg = build_block_message("master", "merge")
    assert "`git merge`" in msg
    assert "master" in msg
    assert "AGENTS.md" in msg
    assert "`git tag`" in msg


def test_build_block_message_unknown_subcommand_is_generic() -> None:
    msg = build_block_message("main", UNKNOWN_BLOCKED_SUBCOMMAND)
    assert "git write operation" in msg
    assert UNKNOWN_BLOCKED_SUBCOMMAND not in msg


def test_emit_deny_payload_shapes() -> None:
    claude = emit_deny_payload("claude", "msg")
    assert claude == {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "msg",
        }
    }
    cursor = emit_deny_payload("cursor", "msg")
    assert cursor == {
        "permission": "deny",
        "user_message": "msg",
        "agent_message": "msg",
    }


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
