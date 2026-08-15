#!/usr/bin/env python3.14
"""Validate rr-planner markdown item headers, graph, status, and items.json drift."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DOC_FILES: dict[str, str] = {
    "exec-summary": "exec-summary.md",
    "mrd": "mrd.md",
    "brd": "brd.md",
    "prd": "prd.md",
    "frd": "frd.md",
}

PREFIX_TO_DOC: dict[str, str] = {
    "ES": "exec-summary",
    "MRD": "mrd",
    "BRD": "brd",
    "PRD": "prd",
    "FRD": "frd",
}

DOC_TO_PREFIX: dict[str, str] = {v: k for k, v in PREFIX_TO_DOC.items()}
PREFIX_LEVEL: dict[str, int] = {"ES": 0, "MRD": 1, "BRD": 2, "PRD": 3, "FRD": 4}
DOC_METHOD: dict[str, str] = {
    "exec-summary": "moscow",
    "mrd": "kano",
    "brd": "moscow",
    "prd": "moscow",
    "frd": "triad",
}

HEADING_RE = re.compile(r"^(#{2,4}) (ES|MRD|BRD|PRD|FRD)-(\d+(?:\.\d+)?): (.+)$")
META_RE = re.compile(r"^- \*\*(.+?):\*\* (.+)$")
ID_RE = re.compile(r"^(ES|MRD|BRD|PRD|FRD)-(\d+)(?:\.(\d+))?$")
_DASH_CLASS = "\u2014\u2013\u2212-"
AXIS_RE = re.compile(
    rf"^(critical|high|moderate|low)\s+[{_DASH_CLASS}]\s+(.+)$",
    re.IGNORECASE,
)

CLOSED_KEYS = frozenset(
    {
        "Parent",
        "Kind",
        "Spec",
        "Build",
        "MoSCoW",
        "Kano",
        "If present",
        "If absent",
        "If wrong",
        "Class",
        "Supersedes",
        "Superseded-by",
    }
)
REQUIRED_KEYS = frozenset({"Parent", "Kind", "Spec"})
FRD_LEAF_KEYS = frozenset({"Build", "If present", "If absent", "If wrong", "Class"})
KIND_VALUES = frozenset({"container", "leaf"})
SPEC_VALUES = frozenset({"idea", "draft", "ready", "deprecated"})
BUILD_VALUES = frozenset({"none", "in_progress", "done"})
MOSCOW_VALUES = frozenset({"Must", "Should", "Could", "Won't"})
KANO_VALUES = frozenset({"basic", "performance", "delighter"})
MAGNITUDE_VALUES = frozenset({"critical", "high", "moderate", "low"})
CLASS_VALUES = frozenset(
    {"must-correct", "must-present", "protect", "leverage", "optional"}
)
HIGH_MAG = frozenset({"critical", "high"})
NULL_SENTINELS = frozenset({"\u2014", "-", "\u2013", "\u2212", "none", "null", ""})
JSON_ITEM_KEYS = frozenset(
    {
        "id",
        "parent",
        "kind",
        "spec",
        "build",
        "supersedes",
        "superseded_by",
        "priority_method",
        "moscow",
        "kano",
        "triad",
        "title",
        "doc",
    }
)

SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "rr-planner"
    / "refs"
    / "schemas"
    / "items.schema.json"
)


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    message: str
    item_id: str | None = None

    def format(self) -> str:
        loc = f" {self.item_id}" if self.item_id else ""
        label = "ERROR" if self.severity == "error" else "WARN"
        return f"{label} [{self.code}]{loc}: {self.message}"


@dataclass
class Axis:
    effect: str
    magnitude: str

    def to_record(self) -> dict[str, str]:
        return {"effect": self.effect, "magnitude": self.magnitude}


@dataclass
class Triad:
    if_present: Axis
    if_absent: Axis
    if_wrong: Axis
    class_name: str

    def to_record(self) -> dict[str, Any]:
        return {
            "if_present": self.if_present.to_record(),
            "if_absent": self.if_absent.to_record(),
            "if_wrong": self.if_wrong.to_record(),
            "class": self.class_name,
        }


@dataclass
class Item:
    id: str
    title: str
    prefix: str
    doc: str
    parent: str | None
    kind: str
    spec: str
    build: str | None = None
    moscow: str | None = None
    kano: str | None = None
    triad: Triad | None = None
    supersedes: str | None = None
    superseded_by: str | None = None
    source_file: str = ""
    raw_keys: set[str] = field(default_factory=set)

    @property
    def parts(self) -> tuple[int, ...]:
        match = ID_RE.match(self.id)
        if not match:
            return ()
        major = int(match.group(2))
        minor = match.group(3)
        if minor is None:
            return (major,)
        return (major, int(minor))

    def to_record(self) -> dict[str, Any]:
        record: dict[str, Any] = {
            "id": self.id,
            "parent": self.parent,
            "kind": self.kind,
            "spec": self.spec,
            "priority_method": DOC_METHOD[self.doc],
            "title": self.title,
            "doc": self.doc,
        }
        if self.build is not None:
            record["build"] = self.build
        if self.supersedes:
            record["supersedes"] = self.supersedes
        if self.superseded_by:
            record["superseded_by"] = self.superseded_by
        method = DOC_METHOD[self.doc]
        if self.kind == "leaf":
            if method == "moscow":
                record["moscow"] = self.moscow
            elif method == "kano":
                record["kano"] = self.kano
            elif self.triad is not None:
                record["triad"] = self.triad.to_record()
        return record


def _null_or_value(raw: str) -> str | None:
    text = raw.strip()
    if text in NULL_SENTINELS:
        return None
    return text


def _parse_axis(raw: str) -> Axis | None:
    match = AXIS_RE.match(raw.strip())
    if not match:
        return None
    return Axis(effect=match.group(2).strip(), magnitude=match.group(1).lower())


def parse_markdown(text: str, source_file: str) -> tuple[list[Item], list[Issue]]:
    issues: list[Issue] = []
    items: list[Item] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        match = HEADING_RE.match(lines[i])
        if not match:
            i += 1
            continue
        prefix = match.group(2)
        number = match.group(3)
        title = match.group(4).strip()
        item_id = f"{prefix}-{number}"
        i += 1
        meta: dict[str, str] = {}
        while i < len(lines) and lines[i].strip():
            meta_match = META_RE.match(lines[i])
            if not meta_match:
                issues.append(
                    Issue(
                        "error",
                        "MALFORMED_META",
                        f"expected '- **Key:** value' under {item_id}, got {lines[i]!r}",
                        item_id,
                    )
                )
                i += 1
                continue
            key, value = meta_match.group(1), meta_match.group(2).strip()
            if key not in CLOSED_KEYS:
                issues.append(
                    Issue(
                        "error", "UNKNOWN_KEY", f"unknown metadata key {key!r}", item_id
                    )
                )
            if key in meta:
                issues.append(
                    Issue(
                        "error",
                        "DUPLICATE_KEY",
                        f"duplicate metadata key {key!r}",
                        item_id,
                    )
                )
            meta[key] = value
            i += 1
        items.append(_item_from_meta(item_id, title, prefix, meta, source_file, issues))
        i += 1
    return items, issues


def _item_from_meta(
    item_id: str,
    title: str,
    prefix: str,
    meta: dict[str, str],
    source_file: str,
    issues: list[Issue],
) -> Item:
    doc = PREFIX_TO_DOC[prefix]
    for key in REQUIRED_KEYS:
        if key not in meta:
            issues.append(
                Issue("error", "MISSING_KEY", f"missing required key {key}", item_id)
            )
    kind = meta.get("Kind", "")
    spec = meta.get("Spec", "")
    if kind and kind not in KIND_VALUES:
        issues.append(
            Issue(
                "error",
                "INVALID_VALUE",
                f"Kind must be container|leaf, got {kind!r}",
                item_id,
            )
        )
    if spec and spec not in SPEC_VALUES:
        issues.append(
            Issue(
                "error",
                "INVALID_VALUE",
                f"Spec must be idea|draft|ready|deprecated, got {spec!r}",
                item_id,
            )
        )
    parent = _null_or_value(meta["Parent"]) if "Parent" in meta else None
    build = _null_or_value(meta["Build"]) if "Build" in meta else None
    if build is not None and build not in BUILD_VALUES:
        issues.append(
            Issue(
                "error",
                "INVALID_VALUE",
                f"Build must be none|in_progress|done, got {build!r}",
                item_id,
            )
        )
    moscow = _null_or_value(meta["MoSCoW"]) if "MoSCoW" in meta else None
    if moscow is not None and moscow not in MOSCOW_VALUES:
        issues.append(
            Issue(
                "error",
                "INVALID_VALUE",
                f"MoSCoW must be Must|Should|Could|Won't, got {moscow!r}",
                item_id,
            )
        )
    kano = _null_or_value(meta["Kano"]) if "Kano" in meta else None
    if kano is not None and kano not in KANO_VALUES:
        issues.append(
            Issue(
                "error",
                "INVALID_VALUE",
                f"Kano must be basic|performance|delighter, got {kano!r}",
                item_id,
            )
        )
    triad: Triad | None = None
    if any(k in meta for k in ("If present", "If absent", "If wrong", "Class")):
        triad = _parse_triad(item_id, meta, issues)
    supersedes = _null_or_value(meta["Supersedes"]) if "Supersedes" in meta else None
    superseded_by = (
        _null_or_value(meta["Superseded-by"]) if "Superseded-by" in meta else None
    )
    return Item(
        id=item_id,
        title=title,
        prefix=prefix,
        doc=doc,
        parent=parent,
        kind=kind,
        spec=spec,
        build=build,
        moscow=moscow,
        kano=kano,
        triad=triad,
        supersedes=supersedes,
        superseded_by=superseded_by,
        source_file=source_file,
        raw_keys=set(meta),
    )


def _parse_triad(
    item_id: str, meta: dict[str, str], issues: list[Issue]
) -> Triad | None:
    axes: dict[str, Axis | None] = {}
    for field_name, key in (
        ("if_present", "If present"),
        ("if_absent", "If absent"),
        ("if_wrong", "If wrong"),
    ):
        if key not in meta:
            axes[field_name] = None
            continue
        axis = _parse_axis(meta[key])
        if axis is None:
            issues.append(
                Issue(
                    "error",
                    "INVALID_VALUE",
                    f"{key} must be '<magnitude> — <effect>'",
                    item_id,
                )
            )
        elif axis.magnitude not in MAGNITUDE_VALUES:
            issues.append(
                Issue(
                    "error",
                    "INVALID_VALUE",
                    f"{key} magnitude {axis.magnitude!r}",
                    item_id,
                )
            )
        axes[field_name] = axis
    class_name = meta.get("Class", "")
    if class_name and class_name not in CLASS_VALUES:
        issues.append(
            Issue(
                "error",
                "INVALID_VALUE",
                f"Class {class_name!r} is not a known class",
                item_id,
            )
        )
    present, absent, wrong = axes["if_present"], axes["if_absent"], axes["if_wrong"]
    if present is None or absent is None or wrong is None or not class_name:
        return None
    return Triad(
        if_present=present, if_absent=absent, if_wrong=wrong, class_name=class_name
    )


def derived_class(present: str, absent: str, wrong: str) -> str:
    hi_a = absent in HIGH_MAG
    hi_w = wrong in HIGH_MAG
    hi_p = present in HIGH_MAG
    if hi_a and hi_w:
        return "must-correct"
    if hi_a:
        return "must-present"
    if hi_w:
        return "protect"
    if hi_p and absent == "low" and wrong == "low":
        return "leverage"
    return "optional"


def parse_planning_dir(planning_dir: Path) -> tuple[list[Item], list[Issue]]:
    items: list[Item] = []
    issues: list[Issue] = []
    found_md = False
    for doc, filename in DOC_FILES.items():
        path = planning_dir / filename
        if not path.is_file():
            continue
        found_md = True
        parsed, parse_issues = parse_markdown(
            path.read_text(encoding="utf-8"), filename
        )
        prefix = DOC_TO_PREFIX[doc]
        for item in parsed:
            if item.prefix != prefix:
                issues.append(
                    Issue(
                        "error",
                        "DOC_PREFIX",
                        f"id prefix {item.prefix} does not belong in {filename}",
                        item.id,
                    )
                )
        items.extend(parsed)
        issues.extend(parse_issues)
    if not found_md:
        issues.append(
            Issue("error", "NO_DOCS", f"no planning markdown files in {planning_dir}")
        )
    return items, issues


def load_items_json(path: Path) -> tuple[list[dict[str, Any]], list[Issue]]:
    if not path.is_file():
        return [], [Issue("error", "MISSING_JSON", f"missing {path.name}")]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [Issue("error", "INVALID_JSON", f"{path.name}: {exc}")]
    if not isinstance(payload, dict) or "items" not in payload:
        return [], [
            Issue(
                "error", "INVALID_JSON", f"{path.name} must be an object with items[]"
            )
        ]
    if not isinstance(payload["items"], list):
        return [], [Issue("error", "INVALID_JSON", "items must be an array")]
    records: list[dict[str, Any]] = []
    issues: list[Issue] = []
    for index, row in enumerate(payload["items"]):
        if not isinstance(row, dict):
            issues.append(
                Issue("error", "INVALID_JSON", f"items[{index}] is not an object")
            )
            continue
        extra = set(row) - JSON_ITEM_KEYS
        item_id = str(row["id"]) if "id" in row else f"items[{index}]"
        for key in extra:
            issues.append(
                Issue("error", "UNKNOWN_KEY", f"json extra key {key!r}", item_id)
            )
        records.append(row)
    return records, issues


def check_unique_and_ids(items: list[Item]) -> list[Issue]:
    issues: list[Issue] = []
    seen: dict[str, Item] = {}
    for item in items:
        if not ID_RE.match(item.id):
            issues.append(
                Issue("error", "INVALID_ID", f"malformed id {item.id!r}", item.id)
            )
        if len(item.parts) > 2:
            issues.append(Issue("error", "DEPTH", "max depth is n.m", item.id))
        if item.id in seen:
            issues.append(Issue("error", "DUPLICATE_ID", "id is not unique", item.id))
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
            issues.append(
                Issue("error", "KIND", "leaf must not have children", item.id)
            )
        if item.kind == "container" and not kids:
            issues.append(
                Issue("error", "KIND", "container must have children", item.id)
            )
        if item.spec == "idea" and kids:
            issues.append(
                Issue(
                    "error",
                    "IDEA_CHILDREN",
                    "idea items must not have children",
                    item.id,
                )
            )
    return issues


def check_parents(items: list[Item]) -> list[Issue]:
    issues: list[Issue] = []
    by_id = {item.id: item for item in items}
    for item in items:
        if len(item.parts) == 2:
            expected = f"{item.prefix}-{item.parts[0]}"
            if item.parent != expected:
                issues.append(
                    Issue(
                        "error",
                        "PARENT_SHAPE",
                        f"nested id must parent {expected}, got {item.parent!r}",
                        item.id,
                    )
                )
            if item.parent not in by_id:
                issues.append(
                    Issue(
                        "error",
                        "BROKEN_PARENT",
                        f"parent {item.parent} does not exist",
                        item.id,
                    )
                )
            continue
        if item.prefix == "ES":
            if item.parent is not None:
                issues.append(
                    Issue(
                        "error",
                        "PARENT_SHAPE",
                        "ES top-level parent must be —",
                        item.id,
                    )
                )
            continue
        if item.parent is None:
            issues.append(
                Issue("error", "BROKEN_PARENT", "missing cross-doc parent", item.id)
            )
            continue
        if item.parent not in by_id:
            issues.append(
                Issue(
                    "error",
                    "BROKEN_PARENT",
                    f"parent {item.parent} does not exist",
                    item.id,
                )
            )
            continue
        parent = by_id[item.parent]
        child_lv = PREFIX_LEVEL[item.prefix]
        parent_lv = PREFIX_LEVEL[parent.prefix]
        if parent_lv != child_lv - 1:
            issues.append(
                Issue(
                    "error",
                    "LEVEL_SKIP",
                    f"parent {parent.id} skips cascade level",
                    item.id,
                )
            )
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
        issues.append(Issue("error", "CYCLE", "parent walk contains a cycle"))
    return issues


def _check_supersede(items: list[Item], by_id: dict[str, Item]) -> list[Issue]:
    issues: list[Issue] = []
    for item in items:
        if item.supersedes:
            if item.supersedes not in by_id:
                issues.append(
                    Issue(
                        "error",
                        "BROKEN_SUPERSEDE",
                        f"supersedes {item.supersedes} does not exist",
                        item.id,
                    )
                )
            else:
                old = by_id[item.supersedes]
                if old.superseded_by != item.id:
                    issues.append(
                        Issue(
                            "error",
                            "SUPERSEDE_PAIR",
                            f"{item.supersedes} must set superseded_by {item.id}",
                            item.id,
                        )
                    )
                if old.spec != "deprecated":
                    issues.append(
                        Issue(
                            "error",
                            "SUPERSEDE_PAIR",
                            f"{old.id} must be spec:deprecated when superseded",
                            old.id,
                        )
                    )
        if item.superseded_by:
            if item.superseded_by not in by_id:
                issues.append(
                    Issue(
                        "error",
                        "BROKEN_SUPERSEDE",
                        f"superseded_by {item.superseded_by} does not exist",
                        item.id,
                    )
                )
            elif by_id[item.superseded_by].supersedes != item.id:
                issues.append(
                    Issue(
                        "error",
                        "SUPERSEDE_PAIR",
                        f"{item.superseded_by} must set supersedes {item.id}",
                        item.id,
                    )
                )
    return issues


def check_numbering(items: list[Item]) -> list[Issue]:
    issues: list[Issue] = []
    top: dict[str, list[int]] = defaultdict(list)
    nested: dict[tuple[str, str], list[int]] = defaultdict(list)
    for item in items:
        if len(item.parts) == 1:
            top[item.prefix].append(item.parts[0])
        elif len(item.parts) == 2:
            nested[(item.prefix, f"{item.prefix}-{item.parts[0]}")].append(
                item.parts[1]
            )
    for prefix, nums in top.items():
        issues.extend(_dense(sorted(nums), prefix))
    for (_prefix, parent), nums in nested.items():
        issues.extend(_dense(sorted(nums), parent))
    return issues


def _dense(nums: list[int], group: str) -> list[Issue]:
    if not nums:
        return []
    expected = list(range(1, len(nums) + 1))
    if nums != expected:
        return [
            Issue(
                "error",
                "NUMBERING",
                f"{group} sibling indices {nums} are not dense 1..{len(nums)}",
            )
        ]
    return []


def check_required_fields(items: list[Item]) -> list[Issue]:
    issues: list[Issue] = []
    for item in items:
        method = DOC_METHOD[item.doc]
        if item.kind == "container":
            if item.build is not None:
                issues.append(
                    Issue("error", "BUILD_SCOPE", "build is FRD leaves only", item.id)
                )
            if (
                item.moscow is not None
                or item.kano is not None
                or item.triad is not None
            ):
                issues.append(
                    Issue(
                        "error", "CONTAINER_RANK", "containers stay unmarked", item.id
                    )
                )
            continue
        if (
            method == "moscow"
            and "MoSCoW" not in item.raw_keys
            and item.source_file != "items.json"
        ):
            issues.append(Issue("error", "MISSING_KEY", "leaf missing MoSCoW", item.id))
        if (
            method == "kano"
            and "Kano" not in item.raw_keys
            and item.source_file != "items.json"
        ):
            issues.append(Issue("error", "MISSING_KEY", "leaf missing Kano", item.id))
        if item.doc == "frd":
            missing = FRD_LEAF_KEYS - item.raw_keys
            if item.source_file != "items.json" and missing:
                for key in sorted(missing):
                    issues.append(
                        Issue(
                            "error", "MISSING_KEY", f"FRD leaf missing {key}", item.id
                        )
                    )
            if item.build is None:
                issues.append(
                    Issue("error", "MISSING_KEY", "FRD leaf missing Build", item.id)
                )
            if item.triad is None and item.spec == "ready":
                issues.append(
                    Issue(
                        "error", "MISSING_KEY", "ready FRD leaf missing triad", item.id
                    )
                )
        elif item.build is not None:
            issues.append(
                Issue("error", "BUILD_SCOPE", "build is FRD leaves only", item.id)
            )
    return issues


def check_status(items: list[Item]) -> list[Issue]:
    issues: list[Issue] = []
    by_id = {item.id: item for item in items}
    for item in items:
        if item.build and item.build not in BUILD_VALUES and item.build is not None:
            continue
        if (
            item.build is not None
            and item.build != "none"
            and (item.kind != "leaf" or item.doc != "frd" or item.spec != "ready")
        ):
            issues.append(
                Issue(
                    "error",
                    "BUILD_GATE",
                    "build != none requires FRD leaf with spec:ready",
                    item.id,
                )
            )
        if item.spec == "deprecated" and item.build == "in_progress":
            issues.append(
                Issue(
                    "warning",
                    "DEPRECATED_BUILD",
                    "deprecated item still build:in_progress",
                    item.id,
                )
            )
        if item.spec == "ready":
            issues.extend(_ready_keys(item, by_id))
    return issues


def _ready_keys(item: Item, by_id: dict[str, Item]) -> list[Issue]:
    issues: list[Issue] = []
    method = DOC_METHOD[item.doc]
    if item.kind == "leaf":
        if (
            method == "moscow"
            and item.source_file == "items.json"
            and "moscow" not in item.raw_keys
        ):
            issues.append(Issue("error", "DOR", "ready leaf missing moscow", item.id))
        if (
            method == "kano"
            and item.source_file == "items.json"
            and "kano" not in item.raw_keys
        ):
            issues.append(Issue("error", "DOR", "ready leaf missing kano", item.id))
        if method == "triad":
            if item.triad is None:
                issues.append(
                    Issue("error", "DOR", "ready FRD leaf missing triad", item.id)
                )
            elif (
                derived_class(
                    item.triad.if_present.magnitude,
                    item.triad.if_absent.magnitude,
                    item.triad.if_wrong.magnitude,
                )
                != item.triad.class_name
            ):
                expected = derived_class(
                    item.triad.if_present.magnitude,
                    item.triad.if_absent.magnitude,
                    item.triad.if_wrong.magnitude,
                )
                issues.append(
                    Issue(
                        "error",
                        "CLASS_MISMATCH",
                        f"Class {item.triad.class_name} does not match derived {expected}",
                        item.id,
                    )
                )
    if item.parent and item.parent in by_id:
        parent = by_id[item.parent]
        if parent.prefix != item.prefix and parent.spec != "ready":
            issues.append(
                Issue(
                    "error",
                    "PARENT_READY",
                    f"ready item requires cross-doc parent spec:ready (got {parent.spec})",
                    item.id,
                )
            )
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
                Issue(
                    "error",
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
                Issue(
                    "error", "DRIFT", "present in items.json but not markdown", item_id
                )
            )
            continue
        if item_id not in json_by_id:
            issues.append(
                Issue(
                    "error", "DRIFT", "present in markdown but not items.json", item_id
                )
            )
            continue
        md_record = md_by_id[item_id].to_record()
        json_row = json_by_id[item_id]
        for key in (
            "id",
            "parent",
            "kind",
            "spec",
            "build",
            "supersedes",
            "superseded_by",
            "moscow",
            "kano",
            "triad",
            "title",
            "doc",
            "priority_method",
        ):
            left = _norm(md_record.get(key))
            right = _norm(json_row.get(key))
            if key not in md_record and key not in json_row:
                continue
            if key not in md_record and json_row.get(key) in (None,):
                continue
            if left != right:
                issues.append(
                    Issue(
                        "error",
                        "DRIFT",
                        f"{key} markdown={left!r} json={right!r}",
                        item_id,
                    )
                )
    return issues


def validate_dir(
    planning_dir: Path,
    *,
    depth: str = "standard",
) -> list[Issue]:
    del depth  # keys required on leaves at every depth; kept for CLI contract
    md_items, issues = parse_planning_dir(planning_dir)
    json_rows, json_issues = load_items_json(planning_dir / "items.json")
    issues.extend(json_issues)
    issues.extend(check_unique_and_ids(md_items))
    issues.extend(check_kind_and_children(md_items))
    issues.extend(check_parents(md_items))
    issues.extend(check_numbering(md_items))
    issues.extend(check_required_fields(md_items))
    issues.extend(check_status(md_items))
    registry = _load_registry(planning_dir / "session-state.json")
    issues.extend(check_revive(md_items, registry))
    if json_rows:
        issues.extend(check_drift(md_items, json_rows))
        for row in json_rows:
            if "priority_method" not in row:
                issues.append(
                    Issue(
                        "error",
                        "MISSING_KEY",
                        "json item missing priority_method",
                        str(row.get("id", "")),
                    )
                )
            elif row.get("priority_method") != DOC_METHOD.get(str(row.get("doc", ""))):
                doc = str(row.get("doc", ""))
                if doc in DOC_METHOD and row.get("priority_method") != DOC_METHOD[doc]:
                    issues.append(
                        Issue(
                            "error",
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


def has_errors(issues: list[Issue]) -> bool:
    return any(issue.severity == "error" for issue in issues)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("planning_dir", type=Path)
    parser.add_argument(
        "--depth",
        choices=("shallow", "standard", "deep"),
        default="standard",
    )
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    args = parser.parse_args(argv)
    if not args.planning_dir.is_dir():
        print(
            f"ERROR [NO_DIR]: {args.planning_dir} is not a directory", file=sys.stderr
        )
        return 1
    if not args.schema.is_file():
        print(f"WARN [SCHEMA_MISSING]: {args.schema} not found", file=sys.stderr)
    issues = validate_dir(args.planning_dir, depth=args.depth)
    for issue in issues:
        stream = sys.stderr if issue.severity == "error" else sys.stdout
        print(issue.format(), file=stream)
    if has_errors(issues):
        print(
            f"{sum(1 for i in issues if i.severity == 'error')} error(s)",
            file=sys.stderr,
        )
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
