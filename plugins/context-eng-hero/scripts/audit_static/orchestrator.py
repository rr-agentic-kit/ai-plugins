from __future__ import annotations

from pathlib import Path

from audit_static.models import AuditContext, CheckResult
from audit_static.runners import RUNNERS


def run_checks(plugin_root: Path, rel_path: str) -> list[CheckResult]:
    loaded = AuditContext.load(plugin_root, rel_path)
    if isinstance(loaded, list):
        return loaded

    results: list[CheckResult] = []
    for runner in RUNNERS:
        results.extend(runner(loaded))
    return results
