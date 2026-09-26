from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any

from errors import GhError

STDERR_SANITIZE_MAX_LINES = 5
STDERR_SANITIZE_MAX_CHARS = 500


def _sanitize_stderr(stderr: str) -> str:
    lines = []
    for line in stderr.splitlines():
        lower = line.lower()
        if "token" in lower or "password" in lower or "bearer" in lower:
            continue
        lines.append(line)
    snippet = "\n".join(lines[:STDERR_SANITIZE_MAX_LINES]).strip()
    return snippet[:STDERR_SANITIZE_MAX_CHARS]


class GhClient:
    def __init__(self, *, env: dict[str, str] | None = None) -> None:
        if shutil.which("gh") is None:
            raise FileNotFoundError("gh not found in PATH")
        self._env = {**os.environ, **(env or {})}

    def cli(self, args: list[str]) -> str:
        result = subprocess.run(
            ["gh", *args],
            capture_output=True,
            text=True,
            check=False,
            env=self._env,
        )
        if result.returncode != 0:
            raise GhError(
                f"gh {' '.join(args)} failed",
                stderr=_sanitize_stderr(result.stderr),
            )
        return result.stdout

    def api(self, path: str, *, method: str = "GET") -> Any:
        result = subprocess.run(
            ["gh", "api", "-X", method, path],
            capture_output=True,
            text=True,
            check=False,
            env=self._env,
        )
        if result.returncode != 0:
            raise GhError(f"gh api failed: {path}", stderr=_sanitize_stderr(result.stderr))
        if not result.stdout.strip():
            return None
        return json.loads(result.stdout)

    def graphql(self, query: str, variables: dict[str, Any] | None = None) -> Any:
        cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
        if variables:
            for key, value in variables.items():
                if isinstance(value, (int, float, bool)):
                    cmd.extend(["-F", f"{key}={json.dumps(value)}"])
                else:
                    cmd.extend(["-f", f"{key}={value}"])
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            env=self._env,
        )
        if result.returncode != 0:
            raise GhError("gh graphql failed", stderr=_sanitize_stderr(result.stderr))
        payload = json.loads(result.stdout)
        if payload.get("errors"):
            raise GhError(str(payload["errors"]))
        return payload.get("data")


def default_gh() -> GhClient:
    return GhClient()
