"""validate_dir orchestrator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .checks import (
    check_drift,
    check_kind_and_children,
    check_numbering,
    check_parents,
    check_required_fields,
    check_revive,
    check_status,
    check_unique_and_ids,
    load_items_json,
)
from .constants import DOC_METHOD, LEDGER_NAME
from .ledger import check_rationale, load_ledger
from .models import Issue
from .parse import parse_planning_dir
from .workspace import check_baselines, check_plan_entry


def validate_dir(
    planning_dir: Path,
    *,
    depth: str = "standard",
    doc_format: str | None = None,
    require_plan_entry: bool = False,
) -> list[Issue]:
    del depth  # ready leaves need a real rank at every depth; kept for CLI contract
    md_items, issues = parse_planning_dir(planning_dir, doc_format=doc_format)
    if any(issue.code in {"UNSUPPORTED_FORMAT", "STALE_FORMAT"} for issue in issues):
        return issues
    ledger, ledger_issues = load_ledger(planning_dir / LEDGER_NAME)
    issues.extend(ledger_issues)
    json_rows, json_issues = load_items_json(planning_dir / "items.json")
    issues.extend(json_issues)
    issues.extend(check_unique_and_ids(md_items))
    issues.extend(check_kind_and_children(md_items))
    issues.extend(check_parents(md_items))
    reserved = (
        ledger.get("reserved_ids")
        if isinstance(ledger, dict) and isinstance(ledger.get("reserved_ids"), dict)
        else None
    )
    issues.extend(check_numbering(md_items, reserved))
    issues.extend(check_required_fields(md_items))
    issues.extend(check_status(md_items))
    issues.extend(check_rationale(md_items, ledger))
    registry = _load_registry(planning_dir / "session-state.json")
    issues.extend(check_revive(md_items, registry))
    issues.extend(check_baselines(planning_dir, md_items))
    if require_plan_entry:
        issues.extend(check_plan_entry(planning_dir))
    if json_rows:
        issues.extend(check_drift(md_items, json_rows))
        for row in json_rows:
            if "priority_method" not in row:
                issues.append(
                    Issue.error(
                        "MISSING_KEY",
                        "json item missing priority_method",
                        str(row.get("id", "")),
                    )
                )
            elif row.get("priority_method") != DOC_METHOD.get(str(row.get("doc", ""))):
                doc = str(row.get("doc", ""))
                if doc in DOC_METHOD and row.get("priority_method") != DOC_METHOD[doc]:
                    issues.append(
                        Issue.error(
                            "PRIORITY_METHOD",
                            f"priority_method must be {DOC_METHOD[doc]} for {doc}",
                            str(row.get("id", "")),
                        )
                    )
    return issues


def _load_registry(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    registry = payload.get("item_registry")
    return registry if isinstance(registry, dict) else None
