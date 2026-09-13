from __future__ import annotations

import json
import sys
from collections.abc import Callable
from typing import Any

from errors import GhError, GitError, GlabError, WorkflowError


def omit_empty(result: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value for key, value in result.items() if value not in ("", None, [], {})
    }


def write(
    command: str,
    *,
    ok: bool,
    result: dict[str, Any] | None = None,
    error: WorkflowError | None = None,
) -> None:
    payload: dict[str, Any] = {
        "command": command,
        "ok": ok,
        "result": result,
        "error": None
        if error is None
        else {"code": error.code, "message": error.message},
    }
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")
    sys.stdout.flush()


def fail(
    command: str, code: str, message: str, *, result: dict[str, Any] | None = None
) -> int:
    write(command, ok=False, result=result, error=WorkflowError(code, message))
    return 1


def succeed(
    command: str, result: dict[str, Any] | None = None, *, exit_code: int = 0
) -> int:
    write(command, ok=True, result=result)
    return exit_code


def fail_exception(
    command: str,
    exc: BaseException,
    *,
    result: dict[str, Any] | None = None,
) -> int:
    if isinstance(exc, FileNotFoundError):
        missing = str(exc)
        code = "gh_not_found" if "gh" in missing else "glab_not_found"
        return fail(command, code, missing, result=result)
    if isinstance(exc, GitError):
        return fail(command, "git_error", str(exc), result=result)
    if isinstance(exc, GlabError):
        return fail(command, "glab_error", str(exc), result=result)
    if isinstance(exc, GhError):
        return fail(command, "gh_error", str(exc), result=result)
    raise exc


def run_guarded(command: str, action: Callable[[], int]) -> int:
    try:
        return action()
    except (FileNotFoundError, GitError, GlabError, GhError) as exc:
        return fail_exception(command, exc)
