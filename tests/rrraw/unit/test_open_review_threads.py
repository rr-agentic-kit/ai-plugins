"""Unit tests for s-gh open-review-threads.sh with a fake gh on PATH."""

from __future__ import annotations

import json
import os
import subprocess
import textwrap
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[3]
    / "plugins"
    / "rrraw"
    / "skills"
    / "s-gh"
    / "scripts"
    / "open-review-threads.sh"
)

SAMPLE_GRAPHQL = {
    "data": {
        "repository": {
            "pullRequest": {
                "reviewThreads": {
                    "nodes": [
                        {
                            "id": "PRRT_open1",
                            "isResolved": False,
                            "path": "src/a.py",
                            "line": 10,
                            "isOutdated": False,
                            "comments": {
                                "nodes": [
                                    {
                                        "author": {"login": "alice"},
                                        "body": "please fix",
                                    }
                                ]
                            },
                        },
                        {
                            "id": "PRRT_resolved",
                            "isResolved": True,
                            "path": "src/b.py",
                            "line": 2,
                            "isOutdated": True,
                            "comments": {
                                "nodes": [
                                    {
                                        "author": {"login": "bob"},
                                        "body": "done",
                                    }
                                ]
                            },
                        },
                        {
                            "id": "PRRT_open2",
                            "isResolved": False,
                            "path": "src/c.py",
                            "line": None,
                            "isOutdated": True,
                            "comments": {
                                "nodes": [
                                    {
                                        "author": {"login": "carol"},
                                        "body": "nit",
                                    }
                                ]
                            },
                        },
                    ]
                }
            }
        }
    }
}


def _write_fake_gh(
    bin_dir: Path, *, pr_number: str = "42", pr_fail: bool = False
) -> None:
    log_path = bin_dir / "gh.log"
    gh = bin_dir / "gh"
    gh.write_text(
        textwrap.dedent(f"""\
            #!/usr/bin/env bash
            set -eu
            LOG="{log_path}"
            printf '%s\\n' "$*" >> "$LOG"
            if [ "$1" = "repo" ] && [ "$2" = "view" ]; then
              printf 'acme/widget\\n'
              exit 0
            fi
            if [ "$1" = "pr" ] && [ "$2" = "view" ]; then
              if [ "{int(pr_fail)}" -eq 1 ]; then
                exit 1
              fi
              printf '{pr_number}\\n'
              exit 0
            fi
            if [ "$1" = "api" ] && [ "$2" = "graphql" ]; then
              query=""
              thread_id=""
              body=""
              while [ $# -gt 0 ]; do
                case "$1" in
                  -f)
                    case "$2" in
                      query=*) query="${{2#query=}}" ;;
                      owner=*) owner="${{2#owner=}}" ;;
                      name=*) name="${{2#name=}}" ;;
                      threadId=*) thread_id="${{2#threadId=}}" ;;
                      body=*) body="${{2#body=}}" ;;
                    esac
                    shift 2
                    ;;
                  -F)
                    case "$2" in
                      number=*) number="${{2#number=}}" ;;
                    esac
                    shift 2
                    ;;
                  *)
                    shift
                    ;;
                esac
              done
              if printf '%s' "$query" | grep -q addPullRequestReviewThreadReply; then
                if printf '%s' "$query" | grep -q resolveReviewThread; then
                  echo "resolveReviewThread must not be called" >&2
                  exit 9
                fi
                printf '%s\\n' '{{"data":{{"addPullRequestReviewThreadReply":{{"comment":{{"id":"IC_reply1"}}}}}}}}'
                exit 0
              fi
              cat <<'JSON'
            {json.dumps(SAMPLE_GRAPHQL)}
            JSON
              exit 0
            fi
            echo "unexpected gh invocation: $*" >&2
            exit 99
            """),
        encoding="utf-8",
    )
    gh.chmod(0o755)


def _run(
    bin_dir: Path,
    *args: str,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    return subprocess.run(
        ["sh", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd) if cwd else None,
        check=False,
    )


@pytest.fixture
def fake_gh(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_fake_gh(bin_dir)
    return bin_dir


def test_defaults_resolve_owner_repo_and_pr(fake_gh: Path, tmp_path: Path) -> None:
    proc = _run(fake_gh, cwd=tmp_path)
    assert proc.returncode == 0
    log = (fake_gh / "gh.log").read_text(encoding="utf-8")
    assert "repo view --json nameWithOwner" in log
    assert "pr view --repo acme/widget --json number" in log
    assert "owner=acme" in log
    assert "name=widget" in log
    assert "number=42" in log


def test_owner_without_repo_exits_2(fake_gh: Path) -> None:
    proc = _run(fake_gh, "--owner", "acme")
    assert proc.returncode == 2
    assert "--owner requires --repo" in proc.stderr


def test_list_stdout_filtered_no_url(fake_gh: Path) -> None:
    proc = _run(fake_gh)
    assert proc.returncode == 0
    rows = json.loads(proc.stdout)
    assert len(rows) == 2
    assert {row["id"] for row in rows} == {"PRRT_open1", "PRRT_open2"}
    for row in rows:
        assert set(row) == {"id", "path", "line", "outdated", "comments"}
        assert "url" not in row
        assert row["comments"]
        assert set(row["comments"][0]) == {"author", "body"}


def test_reply_uses_thread_id_and_does_not_resolve(fake_gh: Path) -> None:
    proc = _run(
        fake_gh,
        "--reply",
        "PRRT_open1",
        "--body",
        "fixed in abc123",
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload == {"thread_id": "PRRT_open1", "comment_id": "IC_reply1"}
    log = (fake_gh / "gh.log").read_text(encoding="utf-8")
    assert "threadId=PRRT_open1" in log
    assert "body=fixed in abc123" in log
    assert "resolveReviewThread" not in log


def test_no_open_pr_exits_1(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_fake_gh(bin_dir, pr_fail=True)
    proc = _run(bin_dir)
    assert proc.returncode == 1
    assert "no open pull request" in proc.stderr
