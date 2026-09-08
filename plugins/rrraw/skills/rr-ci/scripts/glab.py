from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any, Protocol

from errors import GlabError

GLAB_SINGLE_PAGE = 1
GLAB_LIST_PAGE_SIZE = 100
STDERR_SANITIZE_MAX_LINES = 5
STDERR_SANITIZE_MAX_CHARS = 500


class GlabClient(Protocol):
    def api(
        self,
        path: str,
        *,
        method: str = "GET",
        fields: dict[str, str] | None = None,
        input_json: dict[str, Any] | None = None,
    ) -> Any: ...

    def cli(self, args: list[str]) -> str: ...

    def graphql(self, query: str, variables: dict[str, Any] | None = None) -> Any: ...


def _sanitize_stderr(stderr: str) -> str:
    lines = []
    for line in stderr.splitlines():
        lower = line.lower()
        if "token" in lower or "password" in lower or "bearer" in lower:
            continue
        lines.append(line)
    snippet = "\n".join(lines[:STDERR_SANITIZE_MAX_LINES]).strip()
    return snippet[:STDERR_SANITIZE_MAX_CHARS]


def _run_glab(
    cmd: list[str],
    *,
    env: dict[str, str],
    input_payload: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        input=input_payload,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


class _SubprocessGlab:
    def __init__(self, *, env: dict[str, str] | None = None) -> None:
        if shutil.which("glab") is None:
            raise FileNotFoundError("glab not found in PATH")
        self._env = {**os.environ, **(env or {})}

    def _raise_glab_failure(
        self, message: str, result: subprocess.CompletedProcess[str]
    ) -> None:
        raise GlabError(message, stderr=_sanitize_stderr(result.stderr))

    def api(
        self,
        path: str,
        *,
        method: str = "GET",
        fields: dict[str, str] | None = None,
        input_json: dict[str, Any] | None = None,
    ) -> Any:
        cmd = ["glab", "api", path, "--method", method]
        if fields:
            for key, value in fields.items():
                cmd.extend(["-f", f"{key}={value}"])
        payload = None
        if input_json is not None:
            cmd.extend(["--header", "Content-Type: application/json", "--input", "-"])
            payload = json.dumps(input_json)
        result = _run_glab(cmd, env=self._env, input_payload=payload)
        if result.returncode != 0:
            self._raise_glab_failure(f"glab api failed: {path}", result)
        if not result.stdout.strip():
            return None
        return json.loads(result.stdout)

    def cli(self, args: list[str]) -> str:
        result = _run_glab(["glab", *args], env=self._env)
        if result.returncode != 0:
            self._raise_glab_failure(f"glab {' '.join(args)} failed", result)
        return result.stdout

    def graphql(self, query: str, variables: dict[str, Any] | None = None) -> Any:
        env = {**self._env, "GLAB_PAGER": "cat"}
        result = _run_glab(_graphql_cmd(query, variables), env=env)
        if result.returncode != 0:
            self._raise_glab_failure("glab graphql failed", result)
        payload = json.loads(result.stdout)
        return payload.get("data")


def _graphql_cmd(query: str, variables: dict[str, Any] | None = None) -> list[str]:
    cmd = ["glab", "api", "graphql", "-f", f"query={query}"]
    if not variables:
        return cmd
    for key, value in variables.items():
        if value is None:
            continue
        if isinstance(value, (int, float, bool)):
            cmd.extend(["-F", f"{key}={json.dumps(value)}"])
            continue
        cmd.extend(["-f", f"{key}={value}"])
    return cmd


def api_list_pages(
    glab: GlabClient,
    path: str,
    *,
    per_page: int = GLAB_LIST_PAGE_SIZE,
) -> list[Any]:
    """Fetch all pages of a GitLab REST list endpoint (page/per_page)."""
    all_items: list[Any] = []
    page = GLAB_SINGLE_PAGE
    while True:
        separator = "&" if "?" in path else "?"
        page_path = f"{path}{separator}per_page={per_page}&page={page}"
        batch = glab.api(page_path)
        if not isinstance(batch, list):
            raise GlabError(
                f"unexpected API list response for {path} (expected JSON array)"
            )
        all_items.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
    return all_items


def default_glab() -> GlabClient:
    return _SubprocessGlab()
