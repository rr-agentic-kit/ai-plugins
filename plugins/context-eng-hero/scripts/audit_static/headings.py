from __future__ import annotations

import re

HEADING_RE = re.compile(r"^##\s+([^\n]+)$", re.MULTILINE)


def headings_present(body: str) -> set[str]:
    return {m.group(1).strip() for m in HEADING_RE.finditer(body)}
