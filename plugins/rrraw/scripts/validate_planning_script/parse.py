"""Markdown/YAML ingest."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .constants import (
    ATX_HEADING_RE,
    BODY_QUOTE_RE,
    CLOSED_KEYS,
    CONFIDENCE_VALUES,
    DOC_STEMS,
    DOC_TO_PREFIX,
    EFFORT_VALUES,
    GOAL_TYPE_VALUES,
    HEADING_RE,
    ID_RE,
    IMPACT_VALUES,
    INLINE_KEY_RE,
    KANO_VALUES,
    KIND_VALUES,
    LIST_META_RE,
    META_SPLIT_RE,
    MOSCOW_VALUES,
    NULL_SENTINELS,
    PREFIX_TO_DOC,
    RATIONALE_RE,
    REQUIRED_KEYS,
    SPEC_VALUES,
    YAML_KEY_MAP,
    YAML_SKIP_KEYS,
)
from .models import Issue, Item


def _null_or_value(raw: str) -> str | None:
    text = raw.strip()
    if text in NULL_SENTINELS:
        return None
    return text


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
        key = match.group(1)
        value = seg[match.end() :].strip()
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
                Issue.error(
                    "MALFORMED_META",
                    f"expected '_key_: value' under {item_id}, got {detail!r}",
                    item_id,
                )
            )
        elif code == "UNKNOWN_KEY":
            issues.append(
                Issue.error(
                    "UNKNOWN_KEY",
                    f"unknown metadata key {detail!r}",
                    item_id,
                )
            )
        elif code == "DUPLICATE_KEY":
            issues.append(
                Issue.error(
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
                Issue.error(
                    "MALFORMED_META",
                    f"expected '- **Key:** value' under {item_id}, "
                    f"got {lines[index]!r}",
                    item_id,
                )
            )
            index += 1
            continue
        raw_key, value = meta_match.group(1), meta_match.group(2).strip()
        key = _surface_key(raw_key)
        if key is None:
            issues.append(
                Issue.error(
                    "UNKNOWN_KEY",
                    f"unknown metadata key {raw_key!r}",
                    item_id,
                )
            )
            key = raw_key
        if key in meta:
            issues.append(
                Issue.error(
                    "DUPLICATE_KEY",
                    f"duplicate metadata key {key!r}",
                    item_id,
                )
            )
        meta[key] = value
        index += 1
    return meta, index


def _parse_list_meta_block(
    lines: list[str],
    index: int,
    item_id: str,
    issues: list[Issue],
    *,
    migrate: bool,
) -> tuple[dict[str, str], int]:
    meta, index = _consume_list_meta(lines, index, item_id, issues)
    index = _skip_blanks(lines, index)
    if migrate:
        _, index = _capture_free_body(lines, index)
    return meta, index


def _parse_inline_body_block(
    lines: list[str],
    index: int,
    item_id: str,
    issues: list[Issue],
    *,
    migrate: bool,
) -> int:
    if index < len(lines) and BODY_QUOTE_RE.match(lines[index]):
        _, index = _capture_blockquote(lines, index)
        return index
    if index >= len(lines) or not lines[index].strip():
        return index
    if HEADING_RE.match(lines[index]) or ATX_HEADING_RE.match(lines[index]):
        return index
    if LIST_META_RE.match(lines[index]):
        issues.append(
            Issue.error(
                "STALE_FORMAT",
                "list-meta leftover under inline metadata",
                item_id,
            )
        )
        _, index = _consume_list_meta(lines, index, item_id, issues)
        return index
    if migrate:
        _, index = _capture_free_body(lines, index)
        return index
    issues.append(
        Issue.error(
            "BODY_NOT_BLOCKQUOTE",
            "leaf body must be a markdown blockquote (>)",
            item_id,
        )
    )
    _, index = _capture_free_body(lines, index)
    return index


def _parse_item_metadata(
    lines: list[str],
    index: int,
    item_id: str,
    issues: list[Issue],
    *,
    migrate: bool,
) -> tuple[dict[str, str], int]:
    if index >= len(lines):
        issues.append(
            Issue.error(
                "MALFORMED_META",
                f"missing metadata line under {item_id}",
                item_id,
            )
        )
        return {}, index
    if LIST_META_RE.match(lines[index]):
        if not migrate:
            issues.append(
                Issue.error(
                    "STALE_FORMAT",
                    "list-meta (- **Key:**) is stale; "
                    "run validate_planning.sh --rewrite",
                    item_id,
                )
            )
        meta, index = _parse_list_meta_block(
            lines, index, item_id, issues, migrate=migrate
        )
        return meta, index
    if INLINE_KEY_RE.match(lines[index].strip()) or META_SPLIT_RE.search(lines[index]):
        meta, meta_errors = parse_inline_meta_line(lines[index])
        _record_meta_errors(meta_errors, item_id, issues)
        index += 1
        index = _skip_blanks(lines, index)
        index = _parse_inline_body_block(lines, index, item_id, issues, migrate=migrate)
        return meta, index
    issues.append(
        Issue.error(
            "MALFORMED_META",
            f"expected '_key_: value' under {item_id}, got {lines[index]!r}",
            item_id,
        )
    )
    return {}, index + 1


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
        meta, i = _parse_item_metadata(lines, i, item_id, issues, migrate=migrate)
        items.append(_item_from_meta(item_id, title, prefix, meta, source_file, issues))
    return items, issues


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value).strip()


def _yaml_meta_from_raw(
    raw: dict[str, Any], item_id: str, issues: list[Issue]
) -> dict[str, str]:
    meta: dict[str, str] = {}
    for key, value in raw.items():
        if key in YAML_SKIP_KEYS:
            continue
        surface = _surface_key(str(key))
        if surface is None:
            issues.append(
                Issue.error("UNKNOWN_KEY", f"unknown metadata key {key!r}", item_id)
            )
            surface = str(key)
        if surface in meta:
            issues.append(
                Issue.error(
                    "DUPLICATE_KEY",
                    f"duplicate metadata key {surface!r}",
                    item_id,
                )
            )
        meta[surface] = _yaml_scalar(value)
    return meta


def parse_yaml_doc(text: str, source_file: str) -> tuple[list[Item], list[Issue]]:
    issues: list[Issue] = []
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return [], [Issue.error("INVALID_YAML", f"{source_file}: {exc}")]
    if data is None:
        return [], []
    if not isinstance(data, dict):
        return [], [Issue.error("INVALID_YAML", f"{source_file} must be a mapping")]
    items_map = data.get("items")
    if items_map is None:
        items_map = {key: value for key, value in data.items() if ID_RE.match(str(key))}
    if not isinstance(items_map, dict):
        return [], [Issue.error("INVALID_YAML", "items must be a mapping")]
    items: list[Item] = []
    for raw_id, raw in items_map.items():
        item_id = str(raw_id)
        if not isinstance(raw, dict):
            issues.append(
                Issue.error(
                    "INVALID_YAML",
                    f"{item_id} must be a mapping",
                    item_id,
                )
            )
            continue
        title = _yaml_scalar(raw.get("title", ""))
        meta = _yaml_meta_from_raw(raw, item_id, issues)
        match = ID_RE.match(item_id)
        prefix = match.group(1) if match else ""
        if not prefix:
            issues.append(
                Issue.error("INVALID_ID", f"malformed id {item_id!r}", item_id)
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
            Issue.error(
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
            Issue.error(
                "STALE_FORMAT",
                "cascade "
                + ", ".join(f"{stem}.yaml" for stem in yaml_stems)
                + " is stale; run validate_planning.sh --rewrite",
            )
        )
        return None, issues
    return "md", issues


def _validate_enum_field(
    item_id: str,
    meta: dict[str, str],
    meta_key: str,
    allowed: frozenset[str],
    label: str,
    issues: list[Issue],
) -> None:
    if meta_key not in meta:
        return
    value = _null_or_value(meta[meta_key])
    if value is not None and value not in allowed:
        issues.append(
            Issue.error(
                "INVALID_VALUE",
                f"{label} must be {'|'.join(sorted(allowed))}, got {value!r}",
                item_id,
            )
        )


def _validate_item_enums(
    item_id: str, meta: dict[str, str], issues: list[Issue]
) -> None:
    kind = meta.get("kind", "")
    spec = meta.get("spec", "")
    if kind and kind not in KIND_VALUES:
        issues.append(
            Issue.error(
                "INVALID_VALUE",
                f"kind must be container|leaf, got {kind!r}",
                item_id,
            )
        )
    if spec and spec not in SPEC_VALUES:
        issues.append(
            Issue.error(
                "INVALID_VALUE",
                f"spec must be idea|draft|ready|deprecated, got {spec!r}",
                item_id,
            )
        )
    _validate_enum_field(item_id, meta, "moscow", MOSCOW_VALUES, "moscow", issues)
    _validate_enum_field(item_id, meta, "kano", KANO_VALUES, "kano", issues)
    _validate_enum_field(
        item_id, meta, "goal-type", GOAL_TYPE_VALUES, "goal-type", issues
    )
    _validate_enum_field(item_id, meta, "impact", IMPACT_VALUES, "impact", issues)
    _validate_enum_field(
        item_id, meta, "confidence", CONFIDENCE_VALUES, "confidence", issues
    )
    _validate_enum_field(item_id, meta, "effort", EFFORT_VALUES, "effort", issues)


def _optional_meta_value(meta: dict[str, str], key: str) -> str | None:
    return _null_or_value(meta[key]) if key in meta else None


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
                Issue.error("MISSING_KEY", f"missing required key {key}", item_id)
            )
    _validate_item_enums(item_id, meta, issues)
    kind = meta.get("kind", "")
    spec = meta.get("spec", "")
    parent = _optional_meta_value(meta, "parent")
    status = _optional_meta_value(meta, "status")
    tag = _optional_meta_value(meta, "tag")
    moscow = _optional_meta_value(meta, "moscow")
    kano = _optional_meta_value(meta, "kano")
    goal_type = _optional_meta_value(meta, "goal-type")
    reach = _optional_meta_value(meta, "reach")
    impact = _optional_meta_value(meta, "impact")
    confidence = _optional_meta_value(meta, "confidence")
    effort = _optional_meta_value(meta, "effort")
    supersedes = _optional_meta_value(meta, "supersedes")
    superseded_by = _optional_meta_value(meta, "superseded-by")
    rationale = _optional_meta_value(meta, "rationale")
    if rationale is not None and not RATIONALE_RE.match(rationale):
        issues.append(
            Issue.error(
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
        status=status,
        tag=tag,
        goal_type=goal_type,
        reach=reach,
        impact=impact,
        confidence=confidence,
        effort=effort,
        moscow=moscow,
        kano=kano,
        supersedes=supersedes,
        superseded_by=superseded_by,
        rationale=rationale,
        source_file=source_file,
        raw_keys=set(meta),
        raw_meta=dict(meta),
    )


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
                    Issue.error(
                        "DOC_PREFIX",
                        f"id prefix {item.prefix} does not belong in {filename}",
                        item.id,
                    )
                )
        items.extend(parsed)
        issues.extend(parse_issues)
    if not found:
        issues.append(Issue.error("NO_DOCS", f"no planning md files in {planning_dir}"))
    return items, issues
