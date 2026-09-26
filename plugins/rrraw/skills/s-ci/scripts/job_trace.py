from __future__ import annotations

import re

_ERROR_PATTERN = re.compile(
    r"(ERROR|FAILED|Exception|error:|fatal:)",
    re.IGNORECASE,
)
ERROR_LINE_LIMIT = 30


def filter_error_lines(trace: str, *, limit: int = ERROR_LINE_LIMIT) -> list[str]:
    lines = [line for line in trace.splitlines() if _ERROR_PATTERN.search(line)]
    return lines[:limit]
