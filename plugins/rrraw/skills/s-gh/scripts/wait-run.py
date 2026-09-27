#!/usr/bin/env python3
"""Wait for a GitHub Actions workflow run to finish; emit one compact JSON result.

  python3 wait-run.py RUN_ID [--repo OWNER/REPO] [--interval SEC] [--timeout SEC]

Stdout: single JSON object ``{"status": "...", "conclusion": ...}`` when the run
reaches ``status=completed``. Exit 0 on completion (any conclusion). Exit 1 on
timeout; 2 on ``gh`` failure; 3 on malformed JSON or missing fields.

``RUN_ID`` may be passed positionally or via the ``RUN_ID`` environment variable.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from typing import Any

PENDING_STATUSES = frozenset(
    {"queued", "in_progress", "waiting", "requested", "pending"}
)

DEFAULT_INTERVAL = 30
DEFAULT_TIMEOUT = 1800
MIN_INTERVAL = 5
MAX_INTERVAL = 120
MIN_TIMEOUT = 60
MAX_TIMEOUT = 7200

EXIT_TIMEOUT = 1
EXIT_GH = 2
EXIT_JSON = 3


def _bounded_int(value: str, *, lo: int, hi: int, name: str) -> int:
    try:
        parsed = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{name} must be an integer") from None
    if parsed < lo or parsed > hi:
        raise argparse.ArgumentTypeError(
            f"{name} must be between {lo} and {hi} seconds"
        )
    return parsed


def _gh_cmd(run_id: str, repo: str | None) -> list[str]:
    cmd = ["gh", "run", "view", run_id, "--json", "status,conclusion"]
    if repo:
        cmd.extend(["--repo", repo])
    return cmd


def _fetch_run(run_id: str, repo: str | None) -> dict[str, Any]:
    result = subprocess.run(
        _gh_cmd(run_id, repo),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "gh run view failed").strip()
        print(message, file=sys.stderr)
        raise GhCliError(message)
    raw = result.stdout.strip()
    if not raw:
        print("gh run view returned empty output", file=sys.stderr)
        raise JsonError("empty output")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"invalid JSON from gh: {exc}", file=sys.stderr)
        raise JsonError(str(exc)) from exc
    if not isinstance(payload, dict):
        print("gh run view JSON must be an object", file=sys.stderr)
        raise JsonError("expected object")
    if "status" not in payload:
        print("gh run view JSON missing status", file=sys.stderr)
        raise JsonError("missing status")
    return payload


class GhCliError(Exception):
    pass


class JsonError(Exception):
    pass


def wait_for_run(
    run_id: str,
    *,
    repo: str | None = None,
    interval: int = DEFAULT_INTERVAL,
    timeout: int = DEFAULT_TIMEOUT,
    sleep: Any = time.sleep,
    monotonic: Any = time.monotonic,
) -> dict[str, Any]:
    deadline = monotonic() + timeout
    while True:
        payload = _fetch_run(run_id, repo)
        status = str(payload.get("status") or "")
        if status == "completed":
            return {
                "status": status,
                "conclusion": payload.get("conclusion"),
            }
        if status not in PENDING_STATUSES:
            return {
                "status": status,
                "conclusion": payload.get("conclusion"),
            }
        if monotonic() >= deadline:
            raise TimeoutError(status)
        sleep(interval)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Wait for a GitHub Actions run; print one status/conclusion JSON object."
        )
    )
    parser.add_argument(
        "run_id",
        nargs="?",
        default=None,
        help="Workflow run database ID (or set RUN_ID env)",
    )
    parser.add_argument(
        "--repo",
        default=None,
        help="OWNER/REPO when the run is not in the cwd origin repo",
    )
    parser.add_argument(
        "--interval",
        type=lambda v: _bounded_int(
            v, lo=MIN_INTERVAL, hi=MAX_INTERVAL, name="interval"
        ),
        default=DEFAULT_INTERVAL,
        help=(
            f"Poll interval in seconds ({MIN_INTERVAL}-{MAX_INTERVAL}, "
            f"default {DEFAULT_INTERVAL})"
        ),
    )
    parser.add_argument(
        "--timeout",
        type=lambda v: _bounded_int(v, lo=MIN_TIMEOUT, hi=MAX_TIMEOUT, name="timeout"),
        default=DEFAULT_TIMEOUT,
        help=(
            f"Wall timeout in seconds ({MIN_TIMEOUT}-{MAX_TIMEOUT}, "
            f"default {DEFAULT_TIMEOUT})"
        ),
    )
    args = parser.parse_args(argv)

    if shutil.which("gh") is None:
        print("gh not found in PATH", file=sys.stderr)
        return EXIT_GH

    run_id = args.run_id or os.environ.get("RUN_ID")
    if not run_id:
        parser.error(
            "RUN_ID required (positional argument or RUN_ID environment variable)"
        )

    try:
        result = wait_for_run(
            run_id,
            repo=args.repo,
            interval=args.interval,
            timeout=args.timeout,
        )
    except TimeoutError as exc:
        print(
            f"timeout waiting for run {run_id} (last status: {exc.args[0]})",
            file=sys.stderr,
        )
        return EXIT_TIMEOUT
    except GhCliError:
        return EXIT_GH
    except JsonError:
        return EXIT_JSON

    print(json.dumps(result, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
