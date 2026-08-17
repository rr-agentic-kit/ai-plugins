"""Canonical markdown rewrite and directory migrate."""

from __future__ import annotations

from pathlib import Path

import yaml

from .constants import (
    ATX_HEADING_RE,
    BODY_QUOTE_RE,
    CANONICAL_KEY_ORDER,
    DOC_STEMS,
    EM_DASH,
    FRONTMATTER_KEYS,
    HEADING_RE,
    ID_RE,
    INLINE_KEY_RE,
    LIST_META_RE,
    META_SPLIT_RE,
    NATIVE_INDEX_COL,
    NULL_SENTINELS,
)
from .models import Issue, Item
from .parse import (
    _capture_blockquote,
    _capture_free_body,
    _consume_list_meta,
    _item_from_meta,
    _null_or_value,
    _record_meta_errors,
    _skip_blanks,
    _yaml_scalar,
    parse_inline_meta_line,
    parse_yaml_doc,
)


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
        return "", [Issue.error("INVALID_YAML", f"{source_file}: {exc}")]
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return "", [Issue.error("INVALID_YAML", f"{source_file} must be a mapping")]
    items, issues = parse_yaml_doc(text, source_file)
    items_map = data.get("items")
    if not isinstance(items_map, dict):
        items_map = {key: value for key, value in data.items() if ID_RE.match(str(key))}
    bodies: dict[str, str] = {}
    for raw_id, raw in items_map.items():
        if isinstance(raw, dict) and raw.get("body") is not None:
            bodies[str(raw_id)] = str(raw["body"]).strip("\n")
    front = {key: data[key] for key in FRONTMATTER_KEYS if key in data}
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


def rewrite_planning_dir(planning_dir: Path, *, empty_ok: bool = False) -> list[Issue]:
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
            if new_text != text:
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
    if not found and not empty_ok:
        issues.append(Issue.error("NO_DOCS", f"no planning files in {planning_dir}"))
    return issues
