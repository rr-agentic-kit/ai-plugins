"""Unit tests for s-gh wait-run.py with a fake gh on PATH."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import textwrap
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[3]
    / "plugins"
    / "rrraw"
    / "skills"
    / "s-gh"
    / "scripts"
    / "wait-run.py"
)
SCRIPTS = SCRIPT.parent


def _load_wait_run() -> ModuleType:
    spec = importlib.util.spec_from_file_location("wait_run", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_fake_gh(
    bin_dir: Path,
    *,
    responses: list[dict[str, object]] | None = None,
    always_pending: bool = False,
    exit_code: int = 0,
    stdout: str = "",
) -> None:
    log_path = bin_dir / "gh.log"
    counter_path = bin_dir / "gh.counter"
    state_path = bin_dir / "gh.state.json"
    if responses is not None:
        state_path.write_text(json.dumps(responses), encoding="utf-8")
    gh = bin_dir / "gh"
    gh.write_text(
        textwrap.dedent(f"""\
            #!/usr/bin/env bash
            set -eu
            LOG="{log_path}"
            COUNTER="{counter_path}"
            STATE="{state_path}"
            printf '%s\\n' "$*" >> "$LOG"
            if [ "$1" != "run" ] || [ "$2" != "view" ]; then
              echo "unexpected gh invocation: $*" >&2
              exit 99
            fi
            if [ {exit_code} -ne 0 ]; then
              echo "gh failed" >&2
              exit {exit_code}
            fi
            if [ -n "{stdout}" ]; then
              printf '%s' "{stdout}"
              exit 0
            fi
            n=0
            if [ -f "$COUNTER" ]; then
              n=$(cat "$COUNTER")
            fi
            echo $((n + 1)) > "$COUNTER"
            if [ {int(always_pending)} -eq 1 ]; then
              printf '{{"status":"in_progress","conclusion":null}}'
              exit 0
            fi
            python3 - "$n" "$STATE" <<'PY'
            import json, sys
            idx = int(sys.argv[1])
            path = sys.argv[2]
            rows = json.loads(open(path, encoding="utf-8").read())
            print(json.dumps(rows[min(idx, len(rows) - 1)], separators=(",", ":")))
            PY
            """),
        encoding="utf-8",
    )
    gh.chmod(0o755)


def _run(
    bin_dir: Path,
    *args: str,
    env_extra: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["python3", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


@pytest.fixture
def fake_gh(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_fake_gh(
        bin_dir,
        responses=[
            {"status": "in_progress", "conclusion": None},
            {"status": "completed", "conclusion": "success"},
        ],
    )
    return bin_dir


def test_pending_to_completed_emits_one_json_result(fake_gh: Path) -> None:
    proc = _run(fake_gh, "12345", "--interval", "5", "--timeout", "60")
    assert proc.returncode == 0
    assert proc.stdout.strip() == '{"status":"completed","conclusion":"success"}'
    assert proc.stderr == ""
    log = (fake_gh / "gh.log").read_text(encoding="utf-8").splitlines()
    assert len(log) == 2
    assert all("run view 12345 --json status,conclusion" in line for line in log)


def test_failed_conclusion_still_exits_zero(fake_gh: Path) -> None:
    _write_fake_gh(
        fake_gh,
        responses=[{"status": "completed", "conclusion": "failure"}],
    )
    proc = _run(fake_gh, "999", "--interval", "5", "--timeout", "60")
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload == {"status": "completed", "conclusion": "failure"}


def test_repo_forwarding(fake_gh: Path) -> None:
    proc = _run(
        fake_gh,
        "555",
        "--repo",
        "acme/widget",
        "--interval",
        "5",
        "--timeout",
        "60",
    )
    assert proc.returncode == 0
    log = (fake_gh / "gh.log").read_text(encoding="utf-8")
    assert "--repo acme/widget" in log


def test_run_id_from_env(fake_gh: Path) -> None:
    proc = _run(
        fake_gh, "--interval", "5", "--timeout", "60", env_extra={"RUN_ID": "777"}
    )
    assert proc.returncode == 0
    log = (fake_gh / "gh.log").read_text(encoding="utf-8")
    assert "run view 777" in log


def test_timeout_exits_1(monkeypatch: pytest.MonkeyPatch) -> None:
    wait_run = _load_wait_run()

    clock = {"now": 0.0}

    def fake_monotonic() -> float:
        return clock["now"]

    def fake_sleep(seconds: float) -> None:
        clock["now"] += seconds

    monkeypatch.setattr(
        wait_run,
        "_fetch_run",
        lambda run_id, repo: {"status": "in_progress", "conclusion": None},
    )
    with pytest.raises(TimeoutError):
        wait_run.wait_for_run(
            "123",
            interval=5,
            timeout=60,
            sleep=fake_sleep,
            monotonic=fake_monotonic,
        )

    def raise_timeout(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise TimeoutError("in_progress")

    monkeypatch.setattr(wait_run, "wait_for_run", raise_timeout)
    monkeypatch.setattr(wait_run.shutil, "which", lambda _name: "/bin/gh")
    rc = wait_run.main(["123", "--interval", "5", "--timeout", "60"])
    assert rc == wait_run.EXIT_TIMEOUT


def test_gh_cli_failure_exits_2(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_fake_gh(bin_dir, exit_code=1)
    proc = _run(bin_dir, "123", "--interval", "5", "--timeout", "60")
    assert proc.returncode == 2
    assert "gh failed" in proc.stderr
    assert proc.stdout == ""


def test_malformed_json_exits_3(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_fake_gh(bin_dir, stdout="not-json")
    proc = _run(bin_dir, "123", "--interval", "5", "--timeout", "60")
    assert proc.returncode == 3
    assert "invalid JSON" in proc.stderr
    assert proc.stdout == ""
