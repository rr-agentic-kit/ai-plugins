from __future__ import annotations

import json
import sys
from typing import Any


def write(
    command: str,
    *,
    ok: bool,
    result: dict[str, Any] | None = None,
    error: dict[str, str] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "command": command,
        "ok": ok,
        "result": result,
        "error": error,
    }
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")
    sys.stdout.flush()


def succeed(command: str, result: dict[str, Any] | None = None, *, exit_code: int = 0) -> int:
    write(command, ok=True, result=result)
    return exit_code


def fail(command: str, code: str, message: str, *, result: dict[str, Any] | None = None) -> int:
    write(command, ok=False, result=result, error={"code": code, "message": message})
    return 1
