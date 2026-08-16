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

import yaml

DOC_STEMS: tuple[str, ...] = ("exec-summary", "mrd", "brd", "prd", "frd")
YAML_SKIP_KEYS = frozenset(
    {
        "title",
        "body",
        "doc_type",
        "version",
        "created",
        "traces_from",
        "item_index",
    }
)
CANONICAL_KEY_ORDER: tuple[str, ...] = (
    "parent",
    "kind",
    "spec",
    "build",
    "moscow",
    "kano",
    "if-present",
    "if-absent",
    "if-wrong",
    "class",
    "rationale",
    "supersedes",
    "superseded-by",
)
EM_DASH = "\u2014"
NATIVE_INDEX_COL: dict[str, str] = {
    "exec-summary": "MoSCoW",
    "mrd": "Kano",
    "brd": "MoSCoW",
    "prd": "MoSCoW",
    "frd": "Class",
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
LIST_META_RE = re.compile(r"^- \*\*(.+?):\*\* (.+)$")
INLINE_KEY_RE = re.compile(r"^_([a-z][a-z0-9-]*)_:\s*(.*)$")
META_SPLIT_RE = re.compile(r"\s+\|\s+(?=_[a-z][a-z0-9-]*_:)")
BODY_QUOTE_RE = re.compile(r"^> ?(.*)$")
ATX_HEADING_RE = re.compile(r"^#{1,6} ")
ID_RE = re.compile(r"^(ES|MRD|BRD|PRD|FRD)-(\d+)(?:\.(\d+))?$")
RATIONALE_RE = re.compile(r"^r-\d{3,}$")
EVIDENCE_ID_RE = re.compile(r"^e-\d{3,}$")
LEDGER_NAME = "decision-ledger.yaml"
FLIP_KINDS = frozenset({"metric", "fact", "event"})
CONDITION_STRENGTHS = frozenset({"measurable", "observable", "vague"})
RATIONALE_DECISIONS = frozenset({"accept", "reject", "postpone", "pivot"})
RATIONALE_STATUSES = frozenset({"live", "invalidated", "superseded"})
EVIDENCE_STATUSES = frozenset({"supported", "refuted", "unknown", "superseded"})
METRIC_OPS = frozenset({"<", "<=", ">", ">=", "==", "!="})
QUEUE_STATUSES = frozenset({"open", "decided", "dismissed"})
_DASH_CLASS = "\u2014\u2013\u2212-"
AXIS_RE = re.compile(
    rf"^(critical|high|moderate|low)\s+[{_DASH_CLASS}]\s+(.+)$",
    re.IGNORECASE,
)

CLOSED_KEYS = frozenset(CANONICAL_KEY_ORDER)
REQUIRED_KEYS = frozenset({"parent", "kind", "spec"})
FRD_LEAF_KEYS = frozenset({"build", "if-present", "if-absent", "if-wrong", "class"})
YAML_KEY_MAP: dict[str, str] = {
    "Parent": "parent",
    "Kind": "kind",
    "Spec": "spec",
    "Build": "build",
    "MoSCoW": "moscow",
    "Kano": "kano",
    "If present": "if-present",
    "If absent": "if-absent",
    "If wrong": "if-wrong",
    "Class": "class",
    "Rationale": "rationale",
    "Supersedes": "supersedes",
    "Superseded-by": "superseded-by",
}
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
NULL_SENTINELS = frozenset({"\u2014", "-", "\u2013", "\u2212", "null", ""})
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
        "rationale",
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
    rationale: str | None = None
    source_file: str = ""
    raw_keys: set[str] = field(default_factory=set)
    raw_meta: dict[str, str] = field(default_factory=dict)

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
        if self.rationale:
            record["rationale"] = self.rationale
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


def _surface_key(raw_key: str) -> str | None:
    if raw_key in CLOSED_KEYS:
        return raw_key
    return YAML_KEY_MAP.get(raw_key)


def parse_inline_meta_line(line: str) -> tuple[dict[str, str], list[tuple[str, str]]]:
    errors: list[tuple[str, str]] = []
    meta: dict[str, str] = {}
    segments = META_SPLIT_RE.split(line.strip())
    if not segments or not any(seg.strip() for seg in segments):
        return meta, [("MALFORMED_META", line)]
    for raw_seg in segments:
        seg = raw_seg.strip()
        match = INLINE_KEY_RE.match(seg)
        if not match:
            errors.append(("MALFORMED_META", seg))
            continue
        key, value = match.group(1), match.group(2).strip()
        if key not in CLOSED_KEYS:
            errors.append(("UNKNOWN_KEY", key))
        if key in meta:
            errors.append(("DUPLICATE_KEY", key))
        meta[key] = value
    return meta, errors


def _record_meta_errors(
    errors: list[tuple[str, str]], item_id: str, issues: list[Issue]
) -> None:
    for code, detail in errors:
        if code == "MALFORMED_META":
            issues.append(
                Issue(
                    "error",
                    "MALFORMED_META",
                    f"expected '_key_: value' under {item_id}, got {detail!r}",
                    item_id,
                )
            )
        elif code == "UNKNOWN_KEY":
            issues.append(
                Issue(
                    "error",
                    "UNKNOWN_KEY",
                    f"unknown metadata key {detail!r}",
                    item_id,
                )
            )
        elif code == "DUPLICATE_KEY":
            issues.append(
                Issue(
                    "error",
                    "DUPLICATE_KEY",
                    f"duplicate metadata key {detail!r}",
                    item_id,
                )
            )


def _skip_blanks(lines: list[str], index: int) -> int:
    while index < len(lines) and not lines[index].strip():
        index += 1
    return index


def _capture_blockquote(lines: list[str], index: int) -> tuple[str, int]:
    captured: list[str] = []
    while index < len(lines):
        match = BODY_QUOTE_RE.match(lines[index])
        if not match:
            break
        captured.append(match.group(1))
        index += 1
    return "\n".join(captured), index


def _capture_free_body(lines: list[str], index: int) -> tuple[str, int]:
    captured: list[str] = []
    while index < len(lines):
        line = lines[index]
        if HEADING_RE.match(line) or ATX_HEADING_RE.match(line):
            break
        captured.append(line)
        index += 1
    return "\n".join(captured).strip("\n"), index


def _consume_list_meta(
    lines: list[str], index: int, item_id: str, issues: list[Issue]
) -> tuple[dict[str, str], int]:
    meta: dict[str, str] = {}
    while index < len(lines) and lines[index].strip():
        meta_match = LIST_META_RE.match(lines[index])
        if not meta_match:
            issues.append(
                Issue(
                    "error",
                    "MALFORMED_META",
                    f"expected '- **Key:** value' under {item_id}, got {lines[index]!r}",
                    item_id,
                )
            )
            index += 1
            continue
        raw_key, value = meta_match.group(1), meta_match.group(2).strip()
        key = _surface_key(raw_key)
        if key is None:
            issues.append(
                Issue(
                    "error",
                    "UNKNOWN_KEY",
                    f"unknown metadata key {raw_key!r}",
                    item_id,
                )
            )
            key = raw_key
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
        index += 1
    return meta, index


def parse_markdown(
    text: str, source_file: str, *, migrate: bool = False
) -> tuple[list[Item], list[Issue]]:
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
        i = _skip_blanks(lines, i)
        meta: dict[str, str] = {}
        if i >= len(lines):
            issues.append(
                Issue(
                    "error",
                    "MALFORMED_META",
                    f"missing metadata line under {item_id}",
                    item_id,
                )
            )
        elif LIST_META_RE.match(lines[i]):
            if not migrate:
                issues.append(
                    Issue(
                        "error",
                        "STALE_FORMAT",
                        "list-meta (- **Key:**) is stale; run validate_planning.py --rewrite",
                        item_id,
                    )
                )
            meta, i = _consume_list_meta(lines, i, item_id, issues)
            i = _skip_blanks(lines, i)
            if migrate:
                _, i = _capture_free_body(lines, i)
        elif INLINE_KEY_RE.match(lines[i].strip()) or META_SPLIT_RE.search(lines[i]):
            meta, meta_errors = parse_inline_meta_line(lines[i])
            _record_meta_errors(meta_errors, item_id, issues)
            i += 1
            i = _skip_blanks(lines, i)
            if i < len(lines) and BODY_QUOTE_RE.match(lines[i]):
                _, i = _capture_blockquote(lines, i)
            elif (
                i < len(lines)
                and lines[i].strip()
                and not HEADING_RE.match(lines[i])
                and not ATX_HEADING_RE.match(lines[i])
            ):
                if LIST_META_RE.match(lines[i]):
                    issues.append(
                        Issue(
                            "error",
                            "STALE_FORMAT",
                            "list-meta leftover under inline metadata",
                            item_id,
                        )
                    )
                    _, i = _consume_list_meta(lines, i, item_id, issues)
                elif not migrate:
                    issues.append(
                        Issue(
                            "error",
                            "BODY_NOT_BLOCKQUOTE",
                            "leaf body must be a markdown blockquote (>)",
                            item_id,
                        )
                    )
                    _, i = _capture_free_body(lines, i)
                else:
                    _, i = _capture_free_body(lines, i)
        else:
            issues.append(
                Issue(
                    "error",
                    "MALFORMED_META",
                    f"expected '_key_: value' under {item_id}, got {lines[i]!r}",
                    item_id,
                )
            )
            i += 1
        items.append(_item_from_meta(item_id, title, prefix, meta, source_file, issues))
    return items, issues


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value).strip()


def parse_yaml_doc(text: str, source_file: str) -> tuple[list[Item], list[Issue]]:
    issues: list[Issue] = []
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return [], [Issue("error", "INVALID_YAML", f"{source_file}: {exc}")]
    if data is None:
        return [], []
    if not isinstance(data, dict):
        return [], [Issue("error", "INVALID_YAML", f"{source_file} must be a mapping")]
    items_map = data.get("items")
    if items_map is None:
        items_map = {key: value for key, value in data.items() if ID_RE.match(str(key))}
    if not isinstance(items_map, dict):
        return [], [Issue("error", "INVALID_YAML", "items must be a mapping")]
    items: list[Item] = []
    for raw_id, raw in items_map.items():
        item_id = str(raw_id)
        if not isinstance(raw, dict):
            issues.append(
                Issue(
                    "error",
                    "INVALID_YAML",
                    f"{item_id} must be a mapping",
                    item_id,
                )
            )
            continue
        title = _yaml_scalar(raw.get("title", ""))
        meta: dict[str, str] = {}
        for key, value in raw.items():
            if key in YAML_SKIP_KEYS:
                continue
            surface = _surface_key(str(key))
            if surface is None:
                issues.append(
                    Issue(
                        "error", "UNKNOWN_KEY", f"unknown metadata key {key!r}", item_id
                    )
                )
                surface = str(key)
            if surface in meta:
                issues.append(
                    Issue(
                        "error",
                        "DUPLICATE_KEY",
                        f"duplicate metadata key {surface!r}",
                        item_id,
                    )
                )
            meta[surface] = _yaml_scalar(value)
        match = ID_RE.match(item_id)
        prefix = match.group(1) if match else ""
        if not prefix:
            issues.append(
                Issue("error", "INVALID_ID", f"malformed id {item_id!r}", item_id)
            )
            continue
        items.append(_item_from_meta(item_id, title, prefix, meta, source_file, issues))
    return items, issues


def detect_doc_format(
    planning_dir: Path, requested: str | None = None
) -> tuple[str | None, list[Issue]]:
    issues: list[Issue] = []
    if requested is not None and requested != "md":
        issues.append(
            Issue(
                "error",
                "UNSUPPORTED_FORMAT",
                f"format {requested!r} is not a plan document format; use md",
            )
        )
        return None, issues
    yaml_stems = [
        stem for stem in DOC_STEMS if (planning_dir / f"{stem}.yaml").is_file()
    ]
    if yaml_stems:
        issues.append(
            Issue(
                "error",
                "STALE_FORMAT",
                "cascade "
                + ", ".join(f"{stem}.yaml" for stem in yaml_stems)
                + " is stale; run validate_planning.py --rewrite",
            )
        )
        return None, issues
    return "md", issues


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
    kind = meta.get("kind", "")
    spec = meta.get("spec", "")
    if kind and kind not in KIND_VALUES:
        issues.append(
            Issue(
                "error",
                "INVALID_VALUE",
                f"kind must be container|leaf, got {kind!r}",
                item_id,
            )
        )
    if spec and spec not in SPEC_VALUES:
        issues.append(
            Issue(
                "error",
                "INVALID_VALUE",
                f"spec must be idea|draft|ready|deprecated, got {spec!r}",
                item_id,
            )
        )
    parent = _null_or_value(meta["parent"]) if "parent" in meta else None
    build = _null_or_value(meta["build"]) if "build" in meta else None
    if build is not None and build not in BUILD_VALUES:
        issues.append(
            Issue(
                "error",
                "INVALID_VALUE",
                f"build must be none|in_progress|done, got {build!r}",
                item_id,
            )
        )
    moscow = _null_or_value(meta["moscow"]) if "moscow" in meta else None
    if moscow is not None and moscow not in MOSCOW_VALUES:
        issues.append(
            Issue(
                "error",
                "INVALID_VALUE",
                f"moscow must be Must|Should|Could|Won't, got {moscow!r}",
                item_id,
            )
        )
    kano = _null_or_value(meta["kano"]) if "kano" in meta else None
    if kano is not None and kano not in KANO_VALUES:
        issues.append(
            Issue(
                "error",
                "INVALID_VALUE",
                f"kano must be basic|performance|delighter, got {kano!r}",
                item_id,
            )
        )
    triad: Triad | None = None
    if any(k in meta for k in ("if-present", "if-absent", "if-wrong", "class")):
        triad = _parse_triad(item_id, meta, issues)
    supersedes = _null_or_value(meta["supersedes"]) if "supersedes" in meta else None
    superseded_by = (
        _null_or_value(meta["superseded-by"]) if "superseded-by" in meta else None
    )
    rationale = _null_or_value(meta["rationale"]) if "rationale" in meta else None
    if rationale is not None and not RATIONALE_RE.match(rationale):
        issues.append(
            Issue(
                "error",
                "INVALID_VALUE",
                f"rationale must match r-NNN, got {rationale!r}",
                item_id,
            )
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
        rationale=rationale,
        source_file=source_file,
        raw_keys=set(meta),
        raw_meta=dict(meta),
    )


def _parse_triad(
    item_id: str, meta: dict[str, str], issues: list[Issue]
) -> Triad | None:
    axes: dict[str, Axis | None] = {}
    for field_name, key in (
        ("if_present", "if-present"),
        ("if_absent", "if-absent"),
        ("if_wrong", "if-wrong"),
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
    class_name = meta.get("class", "")
    if class_name and class_name not in CLASS_VALUES:
        issues.append(
            Issue(
                "error",
                "INVALID_VALUE",
                f"class {class_name!r} is not a known class",
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


def parse_planning_dir(
    planning_dir: Path, *, doc_format: str | None = None
) -> tuple[list[Item], list[Issue]]:
    fmt, issues = detect_doc_format(planning_dir, doc_format)
    items: list[Item] = []
    if fmt is None:
        return items, issues
    found = False
    for doc in DOC_STEMS:
        filename = f"{doc}.md"
        path = planning_dir / filename
        if not path.is_file():
            continue
        found = True
        text = path.read_text(encoding="utf-8")
        parsed, parse_issues = parse_markdown(text, filename)
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
    if not found:
        issues.append(
            Issue("error", "NO_DOCS", f"no planning md files in {planning_dir}")
        )
    return items, issues


def _display_value(raw: str) -> str:
    if raw.strip() in NULL_SENTINELS:
        return EM_DASH
    return raw.strip()


def format_meta_line(meta: dict[str, str]) -> str:
    parts = [
        f"_{key}_: {_display_value(meta[key])}"
        for key in CANONICAL_KEY_ORDER
        if key in meta
    ]
    return " | ".join(parts)


def wrap_blockquote(body: str) -> str:
    stripped = body.strip("\n")
    if not stripped.strip():
        return ""
    return "\n".join(">" if not line else f"> {line}" for line in stripped.splitlines())


def _meta_for_emit(item: Item) -> dict[str, str]:
    meta = dict(item.raw_meta)
    if "parent" not in meta:
        meta["parent"] = item.parent or EM_DASH
    if "kind" not in meta and item.kind:
        meta["kind"] = item.kind
    if "spec" not in meta and item.spec:
        meta["spec"] = item.spec
    if "rationale" in meta and _null_or_value(meta["rationale"]) is None:
        del meta["rationale"]
    return {key: meta[key] for key in CANONICAL_KEY_ORDER if key in meta}


def rewrite_markdown(text: str, source_file: str) -> tuple[str, list[Issue]]:
    issues: list[Issue] = []
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        match = HEADING_RE.match(lines[i])
        if not match:
            out.append(lines[i])
            i += 1
            continue
        heading_line = lines[i]
        prefix = match.group(2)
        number = match.group(3)
        title = match.group(4).strip()
        item_id = f"{prefix}-{number}"
        i += 1
        i = _skip_blanks(lines, i)
        meta: dict[str, str] = {}
        body = ""
        if i < len(lines) and LIST_META_RE.match(lines[i]):
            meta, i = _consume_list_meta(lines, i, item_id, issues)
            i = _skip_blanks(lines, i)
            body, i = _capture_free_body(lines, i)
        elif i < len(lines) and (
            INLINE_KEY_RE.match(lines[i].strip()) or META_SPLIT_RE.search(lines[i])
        ):
            meta, meta_errors = parse_inline_meta_line(lines[i])
            _record_meta_errors(meta_errors, item_id, issues)
            i += 1
            i = _skip_blanks(lines, i)
            if i < len(lines) and BODY_QUOTE_RE.match(lines[i]):
                body, i = _capture_blockquote(lines, i)
            elif (
                i < len(lines)
                and lines[i].strip()
                and not ATX_HEADING_RE.match(lines[i])
            ):
                body, i = _capture_free_body(lines, i)
        item = _item_from_meta(item_id, title, prefix, meta, source_file, issues)
        out.append(heading_line)
        out.append(format_meta_line(_meta_for_emit(item)))
        if body.strip():
            out.append("")
            out.append(wrap_blockquote(body))
        if i < len(lines) and lines[i].strip():
            out.append("")
    rewritten = "\n".join(out)
    if rewritten and not rewritten.endswith("\n"):
        rewritten += "\n"
    elif not rewritten:
        rewritten = "\n" if text else ""
    return rewritten, issues


def rewrite_yaml_to_md(text: str, source_file: str) -> tuple[str, list[Issue]]:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return "", [Issue("error", "INVALID_YAML", f"{source_file}: {exc}")]
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return "", [Issue("error", "INVALID_YAML", f"{source_file} must be a mapping")]
    items, issues = parse_yaml_doc(text, source_file)
    items_map = data.get("items")
    if not isinstance(items_map, dict):
        items_map = {key: value for key, value in data.items() if ID_RE.match(str(key))}
    bodies: dict[str, str] = {}
    for raw_id, raw in items_map.items():
        if isinstance(raw, dict) and raw.get("body") is not None:
            bodies[str(raw_id)] = str(raw["body"]).strip("\n")
    front = {
        key: data[key]
        for key in ("doc_type", "version", "created", "traces_from")
        if key in data
    }
    traces = front.get("traces_from")
    if isinstance(traces, list):
        front["traces_from"] = [
            path.replace(".yaml", ".md") if isinstance(path, str) else path
            for path in traces
        ]
    stem = Path(source_file).stem
    title = _yaml_scalar(data.get("title", "")) or stem
    out: list[str] = []
    if front:
        dumped = yaml.safe_dump(front, sort_keys=False, allow_unicode=True).rstrip()
        out.extend(["---", dumped, "---", ""])
    out.extend([f"# {title}", ""])
    for item in items:
        hashes = "####" if len(item.parts) == 2 else "###"
        out.append(f"{hashes} {item.id}: {item.title}")
        out.append(format_meta_line(_meta_for_emit(item)))
        body = bodies.get(item.id, "")
        if body.strip():
            out.append("")
            out.append(wrap_blockquote(body))
        out.append("")
    col = NATIVE_INDEX_COL.get(stem, "MoSCoW")
    out.extend(
        [
            "## Item index",
            "",
            f"| ID | Parent | Spec | {col} |",
            "|----|--------|------|--------|",
        ]
    )
    for item in items:
        parent = item.parent or EM_DASH
        native = EM_DASH
        if item.kind == "leaf":
            if col == "MoSCoW":
                native = item.moscow or EM_DASH
            elif col == "Kano":
                native = item.kano or EM_DASH
            elif item.triad is not None:
                native = item.triad.class_name
        out.append(f"| {item.id} | {parent} | {item.spec} | {native} |")
    out.append("")
    return "\n".join(out), issues


def rewrite_planning_dir(planning_dir: Path) -> list[Issue]:
    issues: list[Issue] = []
    found = False
    for stem in DOC_STEMS:
        md_path = planning_dir / f"{stem}.md"
        yaml_path = planning_dir / f"{stem}.yaml"
        if md_path.is_file():
            found = True
            text = md_path.read_text(encoding="utf-8")
            new_text, parse_issues = rewrite_markdown(text, md_path.name)
            issues.extend(parse_issues)
            md_path.write_text(new_text, encoding="utf-8")
            if yaml_path.is_file():
                yaml_path.unlink()
        elif yaml_path.is_file():
            found = True
            text = yaml_path.read_text(encoding="utf-8")
            new_text, parse_issues = rewrite_yaml_to_md(text, yaml_path.name)
            issues.extend(parse_issues)
            if any(
                issue.severity == "error" and issue.code == "INVALID_YAML"
                for issue in parse_issues
            ):
                continue
            md_path.write_text(new_text, encoding="utf-8")
            yaml_path.unlink()
    if not found:
        issues.append(Issue("error", "NO_DOCS", f"no planning files in {planning_dir}"))
    return issues


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


def check_numbering(
    items: list[Item], reserved_ids: dict[str, Any] | None = None
) -> list[Issue]:
    issues: list[Issue] = []
    top: dict[str, list[int]] = defaultdict(list)
    nested: dict[tuple[str, str], list[int]] = defaultdict(list)
    reserved_top, reserved_nested = _reserved_slots(reserved_ids)
    for item in items:
        if len(item.parts) == 1:
            top[item.prefix].append(item.parts[0])
        elif len(item.parts) == 2:
            nested[(item.prefix, f"{item.prefix}-{item.parts[0]}")].append(
                item.parts[1]
            )
    for prefix, nums in top.items():
        occupied = sorted(set(nums) | reserved_top.get(prefix, set()))
        issues.extend(_dense(occupied, prefix))
    for key, nums in nested.items():
        occupied = sorted(set(nums) | reserved_nested.get(key, set()))
        issues.extend(_dense(occupied, key[1]))
    return issues


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
            if isinstance(raw, bool):
                continue
            if isinstance(raw, int):
                top[prefix].add(raw)
            elif isinstance(raw, str) and raw.isdigit():
                top[prefix].add(int(raw))
            elif isinstance(raw, str) and "." in raw:
                major, _, minor = raw.partition(".")
                if major.isdigit() and minor.isdigit():
                    nested[(prefix, f"{prefix}-{major}")].add(int(minor))
    return top, nested


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
                    Issue("error", "MISSING_KEY", "FRD leaf missing build", item.id)
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
        if method == "moscow" and item.moscow is None:
            issues.append(Issue("error", "DOR", "ready leaf missing moscow", item.id))
        if method == "kano" and item.kano is None:
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
                Issue("error", "DRIFT", "present in items.json but not doc", item_id)
            )
            continue
        if item_id not in json_by_id:
            issues.append(
                Issue("error", "DRIFT", "present in doc but not items.json", item_id)
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
            "rationale",
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
                        f"{key} doc={left!r} json={right!r}",
                        item_id,
                    )
                )
    return issues


def is_ranked_leaf(item: Item) -> bool:
    if item.kind != "leaf":
        return False
    method = DOC_METHOD[item.doc]
    if method == "moscow":
        return item.moscow is not None
    if method == "kano":
        return item.kano is not None
    return True


def load_ledger(path: Path) -> tuple[dict[str, Any] | None, list[Issue]]:
    if not path.is_file():
        return None, [
            Issue(
                "warning",
                "LEDGER_MISSING",
                f"missing {path.name}; rationale checks skipped",
            )
        ]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return None, [Issue("error", "LEDGER_MALFORMED", f"{path.name}: {exc}")]
    if not isinstance(data, dict):
        return None, [
            Issue("error", "LEDGER_MALFORMED", f"{path.name} must be a mapping")
        ]
    issues = _check_ledger_shape(data)
    if any(issue.severity == "error" for issue in issues):
        return data, issues
    return data, issues


def _check_ledger_shape(data: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    evidence = data.get("evidence", {})
    rationales = data.get("rationales", {})
    if "evidence" in data and not isinstance(evidence, dict):
        issues.append(Issue("error", "LEDGER_MALFORMED", "evidence must be a mapping"))
        evidence = {}
    if not isinstance(rationales, dict):
        issues.append(
            Issue("error", "LEDGER_MALFORMED", "rationales must be a mapping")
        )
        return issues
    evidence_ids = {
        key for key in evidence if isinstance(key, str) and EVIDENCE_ID_RE.match(key)
    }
    for raw_id, record in evidence.items():
        eid = str(raw_id)
        if not EVIDENCE_ID_RE.match(eid):
            issues.append(
                Issue(
                    "error",
                    "LEDGER_MALFORMED",
                    f"malformed evidence id {eid!r}",
                    eid,
                )
            )
        if not isinstance(record, dict):
            issues.append(
                Issue(
                    "error",
                    "LEDGER_MALFORMED",
                    f"{eid} must be a mapping",
                    eid,
                )
            )
            continue
        status = record.get("status")
        if status is not None and status not in EVIDENCE_STATUSES:
            issues.append(
                Issue(
                    "error",
                    "LEDGER_MALFORMED",
                    f"evidence status {status!r} is not supported|refuted|unknown|superseded",
                    eid,
                )
            )
    for raw_id, record in rationales.items():
        rid = str(raw_id)
        if not RATIONALE_RE.match(rid):
            issues.append(
                Issue(
                    "error",
                    "LEDGER_MALFORMED",
                    f"malformed rationale id {rid!r}",
                    rid,
                )
            )
        if not isinstance(record, dict):
            issues.append(
                Issue(
                    "error",
                    "LEDGER_MALFORMED",
                    f"{rid} must be a mapping",
                    rid,
                )
            )
            continue
        issues.extend(_check_rationale_record(rid, record, evidence_ids))
    graveyard = data.get("graveyard", {})
    if "graveyard" in data and not isinstance(graveyard, dict):
        issues.append(Issue("error", "LEDGER_MALFORMED", "graveyard must be a mapping"))
    reserved = data.get("reserved_ids", {})
    if "reserved_ids" in data and not isinstance(reserved, dict):
        issues.append(
            Issue("error", "LEDGER_MALFORMED", "reserved_ids must be a mapping")
        )
    queue = data.get("re_decision_queue", [])
    if "re_decision_queue" in data and not isinstance(queue, list):
        issues.append(
            Issue(
                "error",
                "LEDGER_MALFORMED",
                "re_decision_queue must be a list",
            )
        )
    else:
        for index, entry in enumerate(queue):
            if not isinstance(entry, dict):
                issues.append(
                    Issue(
                        "error",
                        "LEDGER_MALFORMED",
                        f"re_decision_queue[{index}] must be a mapping",
                    )
                )
                continue
            status = entry.get("status")
            if status is not None and status not in QUEUE_STATUSES:
                issues.append(
                    Issue(
                        "error",
                        "LEDGER_MALFORMED",
                        f"re_decision_queue[{index}] status {status!r}",
                    )
                )
            pointer = entry.get("rationale")
            if pointer and pointer not in rationales:
                issues.append(
                    Issue(
                        "error",
                        "BROKEN_RATIONALE",
                        f"queue points at unknown rationale {pointer}",
                    )
                )
    return issues


def _check_rationale_record(
    rid: str, record: dict[str, Any], evidence_ids: set[str]
) -> list[Issue]:
    issues: list[Issue] = []
    decision = record.get("decision")
    if decision not in RATIONALE_DECISIONS:
        issues.append(
            Issue(
                "error",
                "LEDGER_MALFORMED",
                f"decision must be accept|reject|postpone|pivot, got {decision!r}",
                rid,
            )
        )
    status = record.get("status")
    if status is not None and status not in RATIONALE_STATUSES:
        issues.append(
            Issue(
                "error",
                "LEDGER_MALFORMED",
                f"status must be live|invalidated|superseded, got {status!r}",
                rid,
            )
        )
    strength = record.get("condition_strength")
    if strength is not None and strength not in CONDITION_STRENGTHS:
        issues.append(
            Issue(
                "error",
                "LEDGER_MALFORMED",
                f"condition_strength must be measurable|observable|vague, got {strength!r}",
                rid,
            )
        )
    flips = record.get("flips_when")
    if not isinstance(flips, list) or not flips:
        issues.append(
            Issue(
                "error",
                "LEDGER_MALFORMED",
                "flips_when must be a non-empty list",
                rid,
            )
        )
        return issues
    for index, entry in enumerate(flips):
        if not isinstance(entry, dict):
            issues.append(
                Issue(
                    "error",
                    "LEDGER_MALFORMED",
                    f"flips_when[{index}] must be a mapping",
                    rid,
                )
            )
            continue
        kind = entry.get("kind")
        if kind not in FLIP_KINDS:
            issues.append(
                Issue(
                    "error",
                    "LEDGER_MALFORMED",
                    f"flips_when[{index}] kind must be metric|fact|event, got {kind!r}",
                    rid,
                )
            )
            continue
        if kind == "metric":
            if not entry.get("metric") or entry.get("op") not in METRIC_OPS:
                issues.append(
                    Issue(
                        "error",
                        "LEDGER_MALFORMED",
                        f"flips_when[{index}] metric requires metric and op in {sorted(METRIC_OPS)}",
                        rid,
                    )
                )
            if "value" not in entry:
                issues.append(
                    Issue(
                        "error",
                        "LEDGER_MALFORMED",
                        f"flips_when[{index}] metric requires value",
                        rid,
                    )
                )
        elif kind == "fact":
            pointer = entry.get("evidence")
            if not isinstance(pointer, str) or not EVIDENCE_ID_RE.match(pointer):
                issues.append(
                    Issue(
                        "error",
                        "LEDGER_MALFORMED",
                        f"flips_when[{index}] fact requires evidence e-NNN",
                        rid,
                    )
                )
            elif pointer not in evidence_ids:
                issues.append(
                    Issue(
                        "error",
                        "BROKEN_RATIONALE",
                        f"flips_when[{index}] evidence {pointer} does not exist",
                        rid,
                    )
                )
        elif kind == "event" and not str(entry.get("text") or "").strip():
            issues.append(
                Issue(
                    "error",
                    "LEDGER_MALFORMED",
                    f"flips_when[{index}] event requires text",
                    rid,
                )
            )
    return issues


def check_rationale(items: list[Item], ledger: dict[str, Any] | None) -> list[Issue]:
    if ledger is None:
        return []
    rationales = ledger.get("rationales")
    if not isinstance(rationales, dict):
        return []
    issues: list[Issue] = []
    for item in items:
        if item.kind != "leaf":
            continue
        ranked = is_ranked_leaf(item)
        rid = item.rationale
        if ranked and not rid:
            issues.append(
                Issue(
                    "error",
                    "MISSING_RATIONALE",
                    "ranked leaf missing Rationale",
                    item.id,
                )
            )
            continue
        if not rid:
            continue
        if rid not in rationales:
            issues.append(
                Issue(
                    "error",
                    "BROKEN_RATIONALE",
                    f"rationale {rid} does not exist",
                    item.id,
                )
            )
    return issues


def validate_dir(
    planning_dir: Path,
    *,
    depth: str = "standard",
    doc_format: str | None = None,
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
    parser.add_argument(
        "--format",
        choices=("md", "yaml", "json"),
        default=None,
        dest="doc_format",
        help="Human plan doc extension. yaml and json are rejected (UNSUPPORTED_FORMAT).",
    )
    parser.add_argument(
        "--rewrite",
        action="store_true",
        help="Migrate list-meta and cascade yaml to canonical md.",
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
    if args.rewrite:
        rewrite_issues = rewrite_planning_dir(args.planning_dir)
        for issue in rewrite_issues:
            stream = sys.stderr if issue.severity == "error" else sys.stdout
            print(issue.format(), file=stream)
        if has_errors(rewrite_issues):
            print(
                f"{sum(1 for i in rewrite_issues if i.severity == 'error')} error(s)",
                file=sys.stderr,
            )
            return 1
    issues = validate_dir(
        args.planning_dir, depth=args.depth, doc_format=args.doc_format
    )
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
