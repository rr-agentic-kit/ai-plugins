"""Migrate pre-redesign planning doc shapes during --rewrite."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .constants import (
    ATX_HEADING_RE,
    CANONICAL_KEY_ORDER,
    DOC_STEMS,
    EM_DASH,
    FRONTMATTER_RE,
    HEADING_RE,
    INLINE_KEY_RE,
    LIST_META_RE,
    META_SPLIT_RE,
    NULL_SENTINELS,
    TECH_NAME,
    YAML_KEY_MAP,
)
from .models import Issue
from .parse import parse_inline_meta_line
from .workspace import challenge_doc_stem, challenge_report_path

CHALLENGE_REPORT_NAME = "challenge-report.md"
FRD_STEM = "frd"
FINDING_HEADING_BASE_RE = re.compile(r"^##\s+(bs-\d+)(?:\s+(.*))?$", re.IGNORECASE)
FINDING_HEADING_DOC_RE = re.compile(r"^[—-]\s*([^\s(]+)")
FINDING_HEADING_SEVERITY_RE = re.compile(r"\(([^)]+)\)\s*$")
MOSCOW_SHOULD_COULD_RE = re.compile(r"_moscow_:\s*(Should|Could)\b")
FUNCTIONAL_DELIVERABLES_HEADING = "## Functional deliverables"
RELEASE_PHASING_RE = re.compile(
    r"^##\s+Release phasing\s*$",
    re.IGNORECASE | re.MULTILINE,
)
FINDING_FIELD_RE = re.compile(r"^-\s+\*\*([^*]+):\*\*\s*([^\n]*)$")


def _parse_finding_heading(
    line: str,
) -> tuple[str, str | None, str | None] | None:
    base = FINDING_HEADING_BASE_RE.match(line)
    if not base:
        return None
    finding_id = base.group(1)
    remainder = (base.group(2) or "").strip()
    heading_doc: str | None = None
    severity: str | None = None
    if remainder:
        doc_match = FINDING_HEADING_DOC_RE.match(remainder)
        if doc_match:
            heading_doc = doc_match.group(1)
            remainder = remainder[doc_match.end() :].strip()
        severity_match = FINDING_HEADING_SEVERITY_RE.search(remainder)
        if severity_match:
            severity = severity_match.group(1)
    return finding_id, heading_doc, severity


def _display_value(raw: str) -> str:
    if raw.strip() in NULL_SENTINELS:
        return EM_DASH
    return raw.strip()


def _format_meta_line(meta: dict[str, str]) -> str:
    parts = [
        f"_{key}_: {_display_value(meta[key])}"
        for key in CANONICAL_KEY_ORDER
        if key in meta
    ]
    return " | ".join(parts)


def _wrap_blockquote(body: str) -> str:
    stripped = body.strip("\n")
    if not stripped.strip():
        return ""
    return "\n".join(">" if not line else f"> {line}" for line in stripped.splitlines())


def _normalize_section(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def _section_has_functional_deliverables(text: str) -> bool:
    for line in text.splitlines():
        match = ATX_HEADING_RE.match(line)
        if match and _normalize_section(line.lstrip("#").strip()) == (
            "functional deliverables"
        ):
            return True
    return False


def _has_should_or_could_moscow(text: str) -> bool:
    return MOSCOW_SHOULD_COULD_RE.search(text) is not None


def _is_old_es_shape(text: str) -> bool:
    if _section_has_functional_deliverables(text):
        return False
    return _has_should_or_could_moscow(text)


def _is_old_prd_shape(text: str) -> bool:
    return RELEASE_PHASING_RE.search(text) is not None


@dataclass
class _DocBlock:
    kind: str
    lines: list[str] = field(default_factory=list)
    section: str | None = None
    item_id: str | None = None
    meta: dict[str, str] = field(default_factory=dict)
    body: str = ""


def _parse_meta_line(line: str) -> dict[str, str]:
    if INLINE_KEY_RE.match(line.strip()) or META_SPLIT_RE.search(line):
        meta, _ = parse_inline_meta_line(line)
        return meta
    return {}


def _skip_blank_lines(lines: list[str], index: int) -> int:
    while index < len(lines) and not lines[index].strip():
        index += 1
    return index


def _consume_list_meta(lines: list[str], index: int, block: _DocBlock) -> int:
    while index < len(lines) and LIST_META_RE.match(lines[index]):
        meta_match = LIST_META_RE.match(lines[index])
        if meta_match:
            raw_key = meta_match.group(1).strip()
            key = YAML_KEY_MAP.get(raw_key, raw_key.lower())
            block.meta[key] = meta_match.group(2).strip()
        block.lines.append(lines[index])
        index += 1
    return index


def _consume_item_meta(lines: list[str], index: int, block: _DocBlock) -> int:
    if index >= len(lines):
        return index
    if LIST_META_RE.match(lines[index]):
        return _consume_list_meta(lines, index, block)
    if INLINE_KEY_RE.match(lines[index].strip()) or META_SPLIT_RE.search(lines[index]):
        block.meta = _parse_meta_line(lines[index])
        block.lines.append(lines[index])
        return index + 1
    return index


def _consume_item_body(lines: list[str], index: int) -> tuple[str, int]:
    body_lines: list[str] = []
    while index < len(lines):
        peek = lines[index]
        if HEADING_RE.match(peek) or (
            ATX_HEADING_RE.match(peek) and not peek.startswith("###")
        ):
            break
        body_lines.append(peek)
        index += 1
    return "\n".join(body_lines).strip("\n"), index


def _parse_item_block(
    lines: list[str], index: int, line: str, current_section: str | None
) -> tuple[_DocBlock, int]:
    item_match = HEADING_RE.match(line)
    if not item_match:
        raise ValueError("expected item heading")
    item_id = f"{item_match.group(2)}-{item_match.group(3)}"
    block = _DocBlock(
        kind="item",
        lines=[line],
        section=current_section,
        item_id=item_id,
    )
    index += 1
    index = _skip_blank_lines(lines, index)
    index = _consume_item_meta(lines, index, block)
    block.body, index = _consume_item_body(lines, index)
    return block, index


def _parse_section_block(
    line: str,
) -> tuple[_DocBlock, str | None]:
    title = line.lstrip("#").strip()
    if line.startswith("# ") and not line.startswith("## "):
        return _DocBlock(kind="title", lines=[line]), None
    return _DocBlock(kind="prose", lines=[line], section=title), title


def _split_doc_blocks(text: str) -> tuple[str, list[_DocBlock]]:
    lines = text.splitlines()
    frontmatter = ""
    start = 0
    match = FRONTMATTER_RE.match(text)
    if match:
        frontmatter = match.group(0)
        start = text[: match.end()].count("\n") + 1
    blocks: list[_DocBlock] = []
    current_section: str | None = None
    index = start
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if HEADING_RE.match(line):
            block, index = _parse_item_block(lines, index, line, current_section)
            blocks.append(block)
            continue
        if ATX_HEADING_RE.match(line):
            block, section = _parse_section_block(line)
            if section is not None:
                current_section = section
            blocks.append(block)
            index += 1
            continue
        blocks.append(_DocBlock(kind="text", lines=[line]))
        index += 1
    return frontmatter, blocks


def _strip_moscow_meta(meta: dict[str, str]) -> dict[str, str]:
    return {key: value for key, value in meta.items() if key != "moscow"}


def _render_item_block(block: _DocBlock) -> list[str]:
    out = list(block.lines[:1])
    if block.meta:
        out.append(_format_meta_line(block.meta))
    if block.body.strip():
        out.append("")
        if block.body.lstrip().startswith(">"):
            out.append(block.body)
        else:
            out.append(_wrap_blockquote(block.body))
    return out


def _rebuild_document(frontmatter: str, blocks: list[_DocBlock]) -> str:
    parts: list[str] = []
    if frontmatter:
        parts.append(frontmatter.rstrip("\n"))
    body_lines: list[str] = []
    for block in blocks:
        if block.kind == "item":
            rendered = _render_item_block(block)
            if body_lines and body_lines[-1].strip():
                body_lines.append("")
            body_lines.extend(rendered)
        else:
            if body_lines and body_lines[-1].strip() and block.lines:
                body_lines.append("")
            body_lines.extend(block.lines)
    parts.extend(body_lines)
    text = "\n".join(parts)
    if text and not text.endswith("\n"):
        text += "\n"
    return text


def _functional_deliverables_blocks(
    functional_items: list[_DocBlock],
) -> list[_DocBlock]:
    return [
        _DocBlock(
            kind="prose",
            lines=[FUNCTIONAL_DELIVERABLES_HEADING],
            section="Functional deliverables",
        ),
        *functional_items,
    ]


def _is_es_item(block: _DocBlock) -> bool:
    return (
        block.kind == "item"
        and block.item_id is not None
        and block.item_id.startswith("ES-")
    )


def _should_insert_functional_section(
    block: _DocBlock,
    inserted_functional: bool,
    functional_items: list[_DocBlock],
) -> bool:
    return (
        not inserted_functional
        and block.kind == "prose"
        and block.section is not None
        and _normalize_section(block.section) == "constraints"
        and bool(functional_items)
    )


def _prepare_es_item(block: _DocBlock) -> _DocBlock | None:
    moscow = block.meta.get("moscow") or block.meta.get("MoSCoW")
    if moscow in {"Should", "Could"}:
        return None
    block.meta = _strip_moscow_meta(block.meta)
    block.lines = block.lines[:1]
    return block


def _append_functional_section_if_needed(
    rebuilt: list[_DocBlock], functional_items: list[_DocBlock]
) -> None:
    if not functional_items:
        return
    insert_at = len(rebuilt)
    for idx, block in enumerate(rebuilt):
        if block.kind == "prose" and block.section:
            section_key = _normalize_section(block.section)
            if section_key in {"constraints", "non-goals", "horizons"}:
                insert_at = idx
                break
    rebuilt[insert_at:insert_at] = _functional_deliverables_blocks(functional_items)


def migrate_exec_summary_shape(text: str, source_file: str) -> tuple[str, list[Issue]]:
    if not _is_old_es_shape(text):
        return text, []
    frontmatter, blocks = _split_doc_blocks(text)
    functional_items: list[_DocBlock] = []
    rebuilt: list[_DocBlock] = []
    inserted_functional = False
    for block in blocks:
        if not _is_es_item(block):
            if _should_insert_functional_section(
                block, inserted_functional, functional_items
            ):
                rebuilt.extend(_functional_deliverables_blocks(functional_items))
                inserted_functional = True
            rebuilt.append(block)
            continue
        prepared = _prepare_es_item(block)
        if prepared is None:
            functional_items.append(block)
            continue
        rebuilt.append(prepared)
    if functional_items and not inserted_functional:
        _append_functional_section_if_needed(rebuilt, functional_items)
    migrated = _rebuild_document(frontmatter, rebuilt)
    return migrated, [
        Issue.warn(
            "MIGRATE_ES_SHAPE",
            f"{source_file}: moved Should/Could items to Functional deliverables "
            "and stripped MoSCoW from other ES ranked sections",
        )
    ]


def _drop_release_phasing_section(blocks: list[_DocBlock]) -> list[_DocBlock]:
    out: list[_DocBlock] = []
    skipping = False
    for block in blocks:
        if block.kind == "prose" and block.lines:
            if RELEASE_PHASING_RE.match(block.lines[0]):
                skipping = True
                continue
            skipping = False
        if skipping:
            continue
        out.append(block)
    return out


def migrate_prd_shape(text: str, source_file: str) -> tuple[str, list[Issue]]:
    if not _is_old_prd_shape(text):
        return text, []
    frontmatter, blocks = _split_doc_blocks(text)
    blocks = _drop_release_phasing_section(blocks)
    for block in blocks:
        if (
            block.kind != "item"
            or not block.item_id
            or not block.item_id.startswith("PRD-")
        ):
            continue
        block.meta = _strip_moscow_meta(block.meta)
        block.lines = block.lines[:1]
    migrated = _rebuild_document(frontmatter, blocks)
    return migrated, [
        Issue.warn(
            "NEEDS_RICE_RESCORE",
            f"{source_file}: removed MoSCoW/release phasing; add RICE/RIC factors "
            "manually — migration does not invent scores",
        )
    ]


def _parse_finding_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in lines:
        match = FINDING_FIELD_RE.match(line.strip())
        if match:
            fields[match.group(1).strip().lower()] = match.group(2).strip()
    return fields


def _finding_doc_stem(fields: dict[str, str], heading_doc: str | None) -> str | None:
    for key in ("doc", "target_doc", "doc_ref"):
        stem = challenge_doc_stem(fields.get(key))
        if stem is not None:
            return stem
    return challenge_doc_stem(heading_doc)


def _render_per_doc_challenge_report(
    stem: str,
    findings: list[tuple[str, list[str], dict[str, str]]],
    shared_front: dict[str, str],
) -> str:
    front = dict(shared_front)
    front["doc"] = stem
    dumped = yaml.safe_dump(front, sort_keys=False, allow_unicode=True).rstrip()
    out = ["---", dumped, "---", "", f"# Challenge: {stem}", ""]
    for finding_id, body_lines, fields in findings:
        severity = fields.get("severity", "").strip()
        title = fields.get("finding") or finding_id
        heading = f"## {finding_id}"
        if severity:
            heading += f" ({severity})"
        out.append(heading)
        out.append("")
        if title and title != finding_id:
            out.append(title)
            out.append("")
        for line in body_lines:
            out.append(line)
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def _load_challenge_shared_front(text: str) -> tuple[dict[str, str], str]:
    shared_front: dict[str, str] = {}
    body = text
    match = FRONTMATTER_RE.match(text)
    if match:
        loaded = yaml.safe_load(match.group(1))
        if isinstance(loaded, dict):
            shared_front = {
                key: str(value) for key, value in loaded.items() if key != "doc"
            }
        body = text[match.end() :]
    return shared_front, body


def _flush_challenge_finding(
    grouped: dict[str, list[tuple[str, list[str], dict[str, str]]]],
    finding_id: str | None,
    heading_doc: str | None,
    body_lines: list[str],
    fields: dict[str, str],
) -> None:
    if finding_id is None:
        return
    stem = _finding_doc_stem(fields, heading_doc) or "prd"
    grouped.setdefault(stem, []).append((finding_id, list(body_lines), dict(fields)))


def _collect_challenge_findings(
    body: str,
) -> dict[str, list[tuple[str, list[str], dict[str, str]]]]:
    grouped: dict[str, list[tuple[str, list[str], dict[str, str]]]] = {
        stem: [] for stem in DOC_STEMS
    }
    current_id: str | None = None
    current_heading_doc: str | None = None
    current_body: list[str] = []
    current_fields: dict[str, str] = {}

    def flush() -> None:
        nonlocal current_id, current_heading_doc, current_body, current_fields
        _flush_challenge_finding(
            grouped,
            current_id,
            current_heading_doc,
            current_body,
            current_fields,
        )
        current_id = None
        current_heading_doc = None
        current_body = []
        current_fields = {}

    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        parsed = _parse_finding_heading(line)
        if parsed is not None:
            flush()
            current_id, current_heading_doc, severity = parsed
            if severity:
                current_fields["severity"] = severity
            continue
        if current_id is None:
            continue
        field_match = FINDING_FIELD_RE.match(line.strip())
        if field_match:
            current_fields[field_match.group(1).strip().lower()] = field_match.group(
                2
            ).strip()
        current_body.append(line)
    flush()
    return grouped


def _write_split_challenge_reports(
    planning_dir: Path,
    grouped: dict[str, list[tuple[str, list[str], dict[str, str]]]],
    shared_front: dict[str, str],
    report_path: Path,
) -> list[Issue]:
    written = 0
    for stem, findings in grouped.items():
        if not findings or stem not in DOC_STEMS:
            continue
        target = challenge_report_path(planning_dir, stem)
        target.write_text(
            _render_per_doc_challenge_report(stem, findings, shared_front),
            encoding="utf-8",
        )
        written += 1
    if not written:
        return []
    report_path.unlink()
    return [
        Issue.warn(
            "MIGRATE_CHALLENGE_REPORT",
            f"split {CHALLENGE_REPORT_NAME} into {written} per-doc "
            f"{{stem}}.challenge.report.md file(s)",
        )
    ]


def split_challenge_report(planning_dir: Path) -> list[Issue]:
    report_path = planning_dir / CHALLENGE_REPORT_NAME
    if not report_path.is_file():
        return []
    text = report_path.read_text(encoding="utf-8")
    shared_front, body = _load_challenge_shared_front(text)
    grouped = _collect_challenge_findings(body)
    return _write_split_challenge_reports(
        planning_dir, grouped, shared_front, report_path
    )


def archive_frd_to_tech(planning_dir: Path) -> list[Issue]:
    md_path = planning_dir / f"{FRD_STEM}.md"
    yaml_path = planning_dir / f"{FRD_STEM}.yaml"
    if not md_path.is_file() and not yaml_path.is_file():
        return []
    parts: list[str] = []
    if md_path.is_file():
        parts.append(md_path.read_text(encoding="utf-8").strip("\n"))
        md_path.unlink()
    if yaml_path.is_file():
        parts.append(
            "```yaml\n" + yaml_path.read_text(encoding="utf-8").strip("\n") + "\n```"
        )
        yaml_path.unlink()
    archive = "\n\n".join(part for part in parts if part.strip())
    tech_path = planning_dir / TECH_NAME
    header = f"## Archived from {FRD_STEM}.md\n\n"
    if tech_path.is_file():
        existing = tech_path.read_text(encoding="utf-8").rstrip("\n")
        tech_path.write_text(f"{existing}\n\n{header}{archive}\n", encoding="utf-8")
    else:
        tech_path.write_text(f"# tech\n\n{header}{archive}\n", encoding="utf-8")
    return [
        Issue.warn(
            "FRD_ARCHIVED",
            f"archived {FRD_STEM}.md into {TECH_NAME}; removed frd from cascade docs",
        )
    ]


def migrate_planning_shapes(planning_dir: Path) -> list[Issue]:
    issues: list[Issue] = []
    issues.extend(split_challenge_report(planning_dir))
    issues.extend(archive_frd_to_tech(planning_dir))
    es_path = planning_dir / "exec-summary.md"
    if es_path.is_file():
        text = es_path.read_text(encoding="utf-8")
        migrated, migrate_issues = migrate_exec_summary_shape(text, es_path.name)
        if migrated != text:
            es_path.write_text(migrated, encoding="utf-8")
        issues.extend(migrate_issues)
    prd_path = planning_dir / "prd.md"
    if prd_path.is_file():
        text = prd_path.read_text(encoding="utf-8")
        migrated, migrate_issues = migrate_prd_shape(text, prd_path.name)
        if migrated != text:
            prd_path.write_text(migrated, encoding="utf-8")
        issues.extend(migrate_issues)
    return issues
