from __future__ import annotations

import time
from collections.abc import Callable


def default_sleeper(sleep: Callable[[float], None] | None) -> Callable[[float], None]:
    if sleep is not None:
        return sleep
    return time.sleep


def run(
    predicate: Callable[[], bool],
    *,
    interval: int = 10,
    max_s: int = 600,
    sleep: Callable[[float], None] = time.sleep,
) -> bool:
    deadline = time.monotonic() + max_s
    while time.monotonic() < deadline:
        if predicate():
            return True
        sleep(interval)
    return predicate()
