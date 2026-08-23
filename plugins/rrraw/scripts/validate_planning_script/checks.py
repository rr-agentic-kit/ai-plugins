"""Id, graph, kind, numbering, fields, status, revive, drift."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .constants import (
    DOC_METHOD,
    DOC_TO_PREFIX,
    ID_RE,
    JSON_ITEM_KEYS,
    PREFIX_LEVEL,
)
from .models import Issue, Item


def load_items_json(path: Path) -> tuple[list[dict[str, Any]], list[Issue]]:
    if not path.is_file():
        return [], [Issue.error("MISSING_JSON", f"missing {path.name}")]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [Issue.error("INVALID_JSON", f"{path.name}: {exc}")]
    if not isinstance(payload, dict) or "items" not in payload:
        return [], [
            Issue.error("INVALID_JSON", f"{path.name} must be an object with items[]")
        ]
    if not isinstance(payload["items"], list):
        return [], [Issue.error("INVALID_JSON", "items must be an array")]
    records: list[dict[str, Any]] = []
    issues: list[Issue] = []
    for index, row in enumerate(payload["items"]):
        if not isinstance(row, dict):
            issues.append(
                Issue.error("INVALID_JSON", f"items[{index}] is not an object")
            )
            continue
        extra = set(row) - JSON_ITEM_KEYS
        item_id = str(row["id"]) if "id" in row else f"items[{index}]"
        for key in extra:
            issues.append(
                Issue.error("UNKNOWN_KEY", f"json extra key {key!r}", item_id)
            )
        records.append(row)
    return records, issues


def check_unique_and_ids(items: list[Item]) -> list[Issue]:
    issues: list[Issue] = []
    seen: dict[str, Item] = {}
    for item in items:
        if not ID_RE.match(item.id):
            issues.append(
                Issue.error("INVALID_ID", f"malformed id {item.id!r}", item.id)
            )
        if item.id.count(".") > 1:
            issues.append(Issue.error("DEPTH", "max depth is n.m", item.id))
        if item.id in seen:
            issues.append(Issue.error("DUPLICATE_ID", "id is not unique", item.id))
        seen[item.id] = item
    return issues


def check_kind_and_children(items: list[Item]) -> list[Issue]:
    issues: list[Issue] = []
    children: dict[str, list[Item]] = defaultdict(list)
    by_id = {item.id: item for item in items}
    for item in items:
        if item.parent and item.parent in by_id:
            children[item.parent].append(item)
    for item in items:
        kids = [kid for kid in children.get(item.id, []) if kid.prefix == item.prefix]
        if item.kind == "leaf" and kids:
            issues.append(Issue.error("KIND", "leaf must not have children", item.id))
        if item.kind == "container" and not kids:
            issues.append(Issue.error("KIND", "container must have children", item.id))
        if item.spec == "idea" and kids:
            issues.append(
                Issue.error(
                    "IDEA_CHILDREN",
                    "idea items must not have children",
                    item.id,
                )
            )
    return issues


def _check_nested_parent(item: Item, by_id: dict[str, Item]) -> list[Issue]:
    issues: list[Issue] = []
    expected = f"{item.prefix}-{item.parts[0]}"
    if item.parent != expected:
        issues.append(
            Issue.error(
                "PARENT_SHAPE",
                f"nested id must parent {expected}, got {item.parent!r}",
                item.id,
            )
        )
    if item.parent not in by_id:
        issues.append(
            Issue.error(
                "BROKEN_PARENT",
                f"parent {item.parent} does not exist",
                item.id,
            )
        )
    return issues


def _check_es_parent(item: Item) -> list[Issue]:
    if item.parent is not None:
        return [
            Issue.error(
                "PARENT_SHAPE",
                "ES top-level parent must be —",
                item.id,
            )
        ]
    return []


def _check_cross_doc_parent(item: Item, by_id: dict[str, Item]) -> list[Issue]:
    issues: list[Issue] = []
    if item.parent is None:
        return [Issue.error("BROKEN_PARENT", "missing cross-doc parent", item.id)]
    if item.parent not in by_id:
        return [
            Issue.error(
                "BROKEN_PARENT",
                f"parent {item.parent} does not exist",
                item.id,
            )
        ]
    parent = by_id[item.parent]
    child_lv = PREFIX_LEVEL[item.prefix]
    parent_lv = PREFIX_LEVEL[parent.prefix]
    if parent_lv != child_lv - 1:
        issues.append(
            Issue.error(
                "LEVEL_SKIP",
                f"parent {parent.id} skips cascade level",
                item.id,
            )
        )
    return issues


def check_parents(items: list[Item]) -> list[Issue]:
    issues: list[Issue] = []
    by_id = {item.id: item for item in items}
    for item in items:
        if item.is_nested:
            issues.extend(_check_nested_parent(item, by_id))
            continue
        if item.prefix == "ES":
            issues.extend(_check_es_parent(item))
            continue
        issues.extend(_check_cross_doc_parent(item, by_id))
    issues.extend(_check_cycles(items))
    issues.extend(_check_supersede(items, by_id))
    return issues


def _check_cycles(items: list[Item]) -> list[Issue]:
    by_id = {item.id: item for item in items}
    color: dict[str, int] = {item.id: 0 for item in items}
    issues: list[Issue] = []

    def visit(nid: str) -> bool:
        color[nid] = 1
        parent = by_id[nid].parent
        if parent and parent in by_id:
            if color[parent] == 1:
                return True
            if color[parent] == 0 and visit(parent):
                return True
        color[nid] = 2
        return False

    seen_cycle = False
    for item_id in color:
        if color[item_id] == 0 and visit(item_id):
            seen_cycle = True
            break
    if seen_cycle:
        issues.append(Issue.error("CYCLE", "parent walk contains a cycle"))
    return issues


def _check_supersedes_link(item: Item, by_id: dict[str, Item]) -> list[Issue]:
    if not item.supersedes:
        return []
    if item.supersedes not in by_id:
        return [
            Issue.error(
                "BROKEN_SUPERSEDE",
                f"supersedes {item.supersedes} does not exist",
                item.id,
            )
        ]
    old = by_id[item.supersedes]
    issues: list[Issue] = []
    if old.superseded_by != item.id:
        issues.append(
            Issue.error(
                "SUPERSEDE_PAIR",
                f"{item.supersedes} must set superseded_by {item.id}",
                item.id,
            )
        )
    if old.spec != "deprecated":
        issues.append(
            Issue.error(
                "SUPERSEDE_PAIR",
                f"{old.id} must be spec:deprecated when superseded",
                old.id,
            )
        )
    return issues


def _check_superseded_by_link(item: Item, by_id: dict[str, Item]) -> list[Issue]:
    if not item.superseded_by:
        return []
    if item.superseded_by not in by_id:
        return [
            Issue.error(
                "BROKEN_SUPERSEDE",
                f"superseded_by {item.superseded_by} does not exist",
                item.id,
            )
        ]
    if by_id[item.superseded_by].supersedes != item.id:
        return [
            Issue.error(
                "SUPERSEDE_PAIR",
                f"{item.superseded_by} must set supersedes {item.id}",
                item.id,
            )
        ]
    return []


def _check_supersede(items: list[Item], by_id: dict[str, Item]) -> list[Issue]:
    issues: list[Issue] = []
    for item in items:
        issues.extend(_check_supersedes_link(item, by_id))
        issues.extend(_check_superseded_by_link(item, by_id))
    return issues


def check_numbering(
    items: list[Item], reserved_ids: dict[str, Any] | None = None
) -> list[Issue]:
    issues: list[Issue] = []
    top: dict[str, list[int]] = defaultdict(list)
    nested: dict[tuple[str, str], list[int]] = defaultdict(list)
    reserved_top, reserved_nested = _reserved_slots(reserved_ids)
    for item in items:
        if item.is_nested:
            nested[(item.prefix, f"{item.prefix}-{item.parts[0]}")].append(
                item.parts[1]
            )
        else:
            top[item.prefix].append(item.parts[0])
    for prefix, nums in top.items():
        occupied = sorted(set(nums) | reserved_top.get(prefix, set()))
        issues.extend(_dense(occupied, prefix))
    for key, nums in nested.items():
        occupied = sorted(set(nums) | reserved_nested.get(key, set()))
        issues.extend(_dense(occupied, key[1]))
    return issues


def _add_reserved_raw(
    raw: object,
    prefix: str,
    top: dict[str, set[int]],
    nested: dict[tuple[str, str], set[int]],
) -> None:
    match raw:
        case bool():
            return
        case int():
            top[prefix].add(raw)
        case str() if raw.isdigit():
            top[prefix].add(int(raw))
        case str() if "." in raw:
            major, _, minor = raw.partition(".")
            if major.isdigit() and minor.isdigit():
                nested[(prefix, f"{prefix}-{major}")].add(int(minor))


def _reserved_slots(
    reserved_ids: dict[str, Any] | None,
) -> tuple[dict[str, set[int]], dict[tuple[str, str], set[int]]]:
    top: dict[str, set[int]] = defaultdict(set)
    nested: dict[tuple[str, str], set[int]] = defaultdict(set)
    if not reserved_ids:
        return top, nested
    for stem, values in reserved_ids.items():
        prefix = DOC_TO_PREFIX.get(str(stem))
        if not prefix or not isinstance(values, list):
            continue
        for raw in values:
            _add_reserved_raw(raw, prefix, top, nested)
    return top, nested


def _dense(nums: list[int], group: str) -> list[Issue]:
    if not nums:
        return []
    expected = list(range(1, len(nums) + 1))
    if nums != expected:
        return [
            Issue.error(
                "NUMBERING",
                f"{group} sibling indices {nums} are not dense 1..{len(nums)}",
            )
        ]
    return []


def _check_container_fields(item: Item) -> list[Issue]:
    issues: list[Issue] = []
    if item.status is not None:
        issues.append(
            Issue.error("STATUS_SCOPE", "status is PRD leaves only", item.id)
        )
    if item.moscow is not None or item.kano is not None:
        issues.append(
            Issue.error("CONTAINER_RANK", "containers stay unmarked", item.id)
        )
    return issues


def check_required_fields(items: list[Item]) -> list[Issue]:
    issues: list[Issue] = []
    for item in items:
        if item.kind == "container":
            issues.extend(_check_container_fields(item))
            continue
        if item.doc != "prd" and item.status is not None:
            issues.append(
                Issue.error("STATUS_SCOPE", "status is PRD leaves only", item.id)
            )
    return issues


def check_status(items: list[Item]) -> list[Issue]:
    issues: list[Issue] = []
    by_id = {item.id: item for item in items}
    for item in items:
        if item.spec == "ready":
            issues.extend(_ready_keys(item, by_id))
    return issues


def _check_ready_leaf_rank(item: Item) -> list[Issue]:
    issues: list[Issue] = []
    method = DOC_METHOD[item.doc]
    if method == "moscow" and "moscow" in item.raw_keys and item.moscow is None:
        issues.append(Issue.error("DOR", "ready leaf missing moscow", item.id))
    if method == "kano" and item.kano is None:
        issues.append(Issue.error("DOR", "ready leaf missing kano", item.id))
    if method == "rice":
        if "goal-type" in item.raw_keys and item.goal_type is None:
            issues.append(
                Issue.error("DOR", "ready leaf missing goal-type", item.id)
            )
        rice_keys = ("reach", "impact", "confidence")
        if any(key in item.raw_keys for key in rice_keys):
            for key, value in (
                ("reach", item.reach),
                ("impact", item.impact),
                ("confidence", item.confidence),
            ):
                if key in item.raw_keys and value is None:
                    issues.append(
                        Issue.error("DOR", f"ready leaf missing {key}", item.id)
                    )
            if "effort" in item.raw_keys and item.effort is None:
                issues.append(
                    Issue.error("DOR", "ready leaf missing effort", item.id)
                )
    return issues


def _check_ready_parent(item: Item, by_id: dict[str, Item]) -> list[Issue]:
    if not item.parent or item.parent not in by_id:
        return []
    parent = by_id[item.parent]
    if parent.prefix == item.prefix or parent.spec == "ready":
        return []
    return [
        Issue.error(
            "PARENT_READY",
            "ready item requires cross-doc parent spec:ready "
            f"(got {parent.spec})",
            item.id,
        )
    ]


def _ready_keys(item: Item, by_id: dict[str, Item]) -> list[Issue]:
    issues: list[Issue] = []
    if item.kind == "leaf":
        issues.extend(_check_ready_leaf_rank(item))
    issues.extend(_check_ready_parent(item, by_id))
    return issues


def check_revive(items: list[Item], previous: dict[str, Any] | None) -> list[Issue]:
    if not previous:
        return []
    issues: list[Issue] = []
    by_id = {item.id: item for item in items}
    for item_id, row in previous.items():
        if not isinstance(row, dict):
            continue
        if row.get("spec") != "deprecated":
            continue
        current = by_id.get(item_id)
        if current is not None and current.spec != "deprecated":
            issues.append(
                Issue.error(
                    "REVIVE",
                    "deprecated is terminal; revive requires a new id",
                    item_id,
                )
            )
    return issues


def _norm(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _norm(value[key]) for key in sorted(value)}
    return value


_DRIFT_KEYS = (
    "id",
    "parent",
    "kind",
    "spec",
    "status",
    "tag",
    "goal_type",
    "reach",
    "impact",
    "confidence",
    "effort",
    "supersedes",
    "superseded_by",
    "moscow",
    "kano",
    "rationale",
    "title",
    "doc",
    "priority_method",
)


def _compare_drift_field(
    item_id: str,
    key: str,
    md_record: dict[str, Any],
    json_row: dict[str, Any],
) -> Issue | None:
    left = _norm(md_record.get(key))
    right = _norm(json_row.get(key))
    if key not in md_record and key not in json_row:
        return None
    if key not in md_record and json_row.get(key) in (None,):
        return None
    if left == right:
        return None
    return Issue.error(
        "DRIFT",
        f"{key} doc={left!r} json={right!r}",
        item_id,
    )


def check_drift(md_items: list[Item], json_rows: list[dict[str, Any]]) -> list[Issue]:
    issues: list[Issue] = []
    md_by_id = {item.id: item for item in md_items}
    json_by_id: dict[str, dict[str, Any]] = {}
    for row in json_rows:
        item_id = str(row.get("id", ""))
        if item_id:
            json_by_id[item_id] = row
    for item_id in sorted(set(md_by_id) | set(json_by_id)):
        if item_id not in md_by_id:
            issues.append(
                Issue.error("DRIFT", "present in items.json but not doc", item_id)
            )
            continue
        if item_id not in json_by_id:
            issues.append(
                Issue.error("DRIFT", "present in doc but not items.json", item_id)
            )
            continue
        md_record = md_by_id[item_id].to_record()
        json_row = json_by_id[item_id]
        for key in _DRIFT_KEYS:
            drift = _compare_drift_field(item_id, key, md_record, json_row)
            if drift is not None:
                issues.append(drift)
    return issues
