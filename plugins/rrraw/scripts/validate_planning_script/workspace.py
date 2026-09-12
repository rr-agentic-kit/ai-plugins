"""status.yaml, frontmatter, mint hash, challenge, baselines."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from .constants import (
    BUSINESS_CASE_NAME,
    BUSINESS_CASE_REQUIRED_FIELDS,
    CHALLENGE_KEYS,
    DISCOVERY_DIR,
    DISCOVERY_STEMS,
    DOC_STEMS,
    DOCS_ROOT_NAME,
    EXECUTE_SLICE_NAME,
    EXECUTE_SLICE_REQUIRED_FIELDS,
    FRONTMATTER_KEYS,
    FRONTMATTER_RE,
    LEGACY_DOC_STEMS,
    LEGACY_PLANS_DIR,
    MATURITY_VALUES,
    PARENT_DOC,
    PHASE_DIRS,
    PLAN_DIR,
    PLAN_STEMS,
    RR_DIR,
    RRR_STATUS_NAME,
    STATUS_NAME,
    STUB_FRONTMATTER_KEYS,
    TASKS_DIR,
    TRACK_DIR_RE,
    canonicalize_doc_stem,
    matches_created_ts,
)
from .models import Issue, Item

_UNFROZEN_REV = "0.1.0?"
_PINS_DELTA_PATHS = "pins.delta_paths"


def find_repo_root(start: Path) -> Path:
    for candidate in (start.resolve(), *start.resolve().parents):
        if (candidate / ".git").exists():
            return candidate
    return start.resolve()


def resolve_within_root(path: Path, root: Path) -> Path:
    """Confine path under root using resolve + prefix check (Sonar S2083 sanitizer)."""
    resolved = path.resolve()
    root_resolved = root.resolve()
    resolved_s = str(resolved)
    root_s = str(root_resolved)
    if resolved_s != root_s and not resolved_s.startswith(f"{root_s}{os.sep}"):
        raise ValueError(f"{path} is outside repo root {root}")
    return resolved


def resolve_planning_dir(planning_dir: Path) -> Path:
    return resolve_within_root(planning_dir, find_repo_root(planning_dir))


def planning_doc_path(planning_dir: Path, stem: str, *, suffix: str = ".md") -> Path:
    if stem not in DOC_STEMS:
        raise ValueError(f"invalid planning doc stem: {stem!r}")
    path = (planning_dir / f"{stem}{suffix}").resolve()
    root = planning_dir.resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"{path} is outside planning dir {root}")
    return path


def challenge_report_path(planning_dir: Path, stem: str) -> Path:
    return planning_doc_path(planning_dir, stem, suffix=".challenge.report.md")


def docs_root(repo_root: Path, *, override: Path | None = None) -> Path:
    if override is not None:
        return resolve_within_root(override, repo_root)
    return resolve_within_root(repo_root / DOCS_ROOT_NAME, repo_root)


def rr_root(docs: Path) -> Path:
    """``docs/rr/`` — rrraw-owned tree (parking + versioned phase dirs)."""
    return docs / RR_DIR


def tasks_dir(docs: Path) -> Path:
    """``docs/rr/tasks/`` — reserved global task tree (not CoW'd on open-next)."""
    return rr_root(docs) / TASKS_DIR


def rrr_status_path(docs: Path) -> Path:
    """Canonical summary path: ``docs/rr/rrr-status.yaml``."""
    return rr_root(docs) / RRR_STATUS_NAME


def track_phase_dir(docs: Path, track: str, phase: str) -> Path:
    """``docs/rr/{track}/{phase}/`` (phase is ``discovery`` or ``plan``)."""
    return rr_root(docs) / track / phase


def find_rrr_status_path(docs: Path) -> Path | None:
    """Prefer ``docs/rr/rrr-status.yaml``; else legacy ``docs/rrr-status.yaml``."""
    for path in (rrr_status_path(docs), docs / RRR_STATUS_NAME):
        if path.is_file():
            return path
    return None


def current_track(docs: Path) -> str:
    """Track from rrr-status (new or legacy path); default ``0.1``."""
    path = find_rrr_status_path(docs)
    if path is not None:
        data, _ = load_status(path)
        if data is not None:
            raw = data.get("track")
            if raw is not None and str(raw).strip():
                return str(raw).strip()
    return "0.1"


def phase_root(planning_dir: Path) -> Path:
    """Phase directory that owns ``status.yaml`` (``discovery/`` or ``plan/``).

    Walks up until ``status.yaml`` exists. Under version-first layout the phase
    parent is a track dir matching ``TRACK_DIR_RE``. Accepts legacy
    ``docs/plans/`` and phase-first ``docs/{phase}/`` when those still have a
    local status.yaml.
    """
    current = planning_dir.resolve()
    for candidate in (current, *current.parents):
        if (candidate / STATUS_NAME).is_file():
            return candidate
    return planning_dir


def plans_root(planning_dir: Path) -> Path:
    """Alias for :func:`phase_root` (legacy name kept for callers/tests)."""
    return phase_root(planning_dir)


def track_for_phase(planning_dir: Path) -> str | None:
    """Track dir name when phase lives under ``docs/rr/{track}/{phase}/``."""
    root = phase_root(planning_dir)
    parent = root.parent
    if TRACK_DIR_RE.fullmatch(parent.name):
        return parent.name
    return None


def find_phase_status_path(phase_dir: Path) -> Path | None:
    path = phase_root(phase_dir) / STATUS_NAME
    return path if path.is_file() else None


def find_status_path(planning_dir: Path) -> Path | None:
    return find_phase_status_path(planning_dir)


def phase_name(planning_dir: Path) -> str | None:
    root = phase_root(planning_dir)
    if root.name in PHASE_DIRS:
        return root.name
    if root.name == LEGACY_PLANS_DIR:
        return LEGACY_PLANS_DIR
    return None


def stems_for_dir(planning_dir: Path) -> tuple[str, ...]:
    name = phase_name(planning_dir)
    if name == DISCOVERY_DIR:
        return DISCOVERY_STEMS
    if name == PLAN_DIR:
        return PLAN_STEMS
    return DOC_STEMS


def discovery_dir_for(planning_dir: Path) -> Path | None:
    """Sibling discovery phase under the same track (or legacy phase-first).

    Version-first: ``docs/rr/{track}/plan`` → ``docs/rr/{track}/discovery``.
    Legacy phase-first: ``docs/plan`` → ``docs/discovery`` (migration window).
    """
    root = phase_root(planning_dir)
    if root.name == PLAN_DIR:
        candidate = root.parent / DISCOVERY_DIR
        return candidate if candidate.is_dir() else None
    if root.name == DISCOVERY_DIR:
        return root
    return None


def default_rrr_status(
    injection_version: int,
    *,
    phase: str = "discovery",
    summary: str = "Discovering — not started",
) -> dict[str, Any]:
    return {
        "claude_config_version": injection_version,
        "track": "0.1",
        "phase": phase,
        "product": _UNFROZEN_REV,
        "docs": _UNFROZEN_REV,
        "discovery_complete": False,
        "docs_shipped": False,
        "product_status": "?",
        "next": None,
        "summary": summary,
    }


def load_status(path: Path) -> tuple[dict[str, Any] | None, list[Issue]]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return None, [Issue.error("HAND_BUMP", f"{path.name}: {exc}")]
    if not isinstance(data, dict):
        return None, [Issue.error("HAND_BUMP", f"{path.name} must be a mapping")]
    return data, []


def write_status_yaml(path: Path, data: dict[str, Any]) -> None:
    dumped = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    path.write_text(dumped, encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, Any]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    data = yaml.safe_load(match.group(1))
    return data if isinstance(data, dict) else {}


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    data = yaml.safe_load(match.group(1))
    fm = data if isinstance(data, dict) else {}
    return fm, text[match.end() :]


def _utc_now_stamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _preserve_created(raw: Any) -> str:
    if isinstance(raw, datetime):
        stamp = raw if raw.tzinfo is not None else raw.replace(tzinfo=UTC)
        return stamp.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(raw, str) and matches_created_ts(raw):
        return raw.strip()
    return _utc_now_stamp()


def _frontmatter_pins(stem: str, levels: dict[str, Any]) -> dict[str, Any]:
    parent = PARENT_DOC.get(stem)
    if parent is None:
        return {}
    raw_row = levels.get(stem)
    row: dict[str, Any] = raw_row if isinstance(raw_row, dict) else {}
    raw_pins = row.get("pins")
    child_pins: dict[str, Any] = raw_pins if isinstance(raw_pins, dict) else {}
    parent_pin = child_pins.get(parent)
    raw_parent = levels.get(parent)
    parent_row: dict[str, Any] = raw_parent if isinstance(raw_parent, dict) else {}
    parent_rev = parent_row.get("rev")
    if isinstance(parent_pin, dict) and is_frozen_rev(parent_rev):
        return {
            parent: {
                "rev": parent_pin.get("rev", parent_rev),
                "digest": parent_pin.get("digest"),
            }
        }
    if is_frozen_rev(parent_rev):
        return {
            parent: {
                "rev": parent_rev,
                "digest": parent_row.get("digest"),
            }
        }
    return {}


def _frontmatter_for_doc(stem: str, status: dict[str, Any] | None) -> dict[str, Any]:
    track = "0.1"
    rev: Any = "?"
    pins: dict[str, Any] = {}
    maturity: str | None = None
    if status is not None:
        raw_track = status.get("track")
        if raw_track is not None and str(raw_track).strip():
            track = str(raw_track)
        raw_levels = status.get("levels")
        levels: dict[str, Any] = raw_levels if isinstance(raw_levels, dict) else {}
        raw_row = levels.get(stem)
        row: dict[str, Any] = raw_row if isinstance(raw_row, dict) else {}
        status_rev = row.get("rev")
        if is_frozen_rev(status_rev):
            rev = status_rev
        pins = _frontmatter_pins(stem, levels)
        raw_maturity = row.get("maturity")
        if isinstance(raw_maturity, str) and raw_maturity in MATURITY_VALUES:
            maturity = raw_maturity
    result: dict[str, Any] = {
        "doc_type": stem,
        "track": track,
        "doc_rev": rev,
        "pins": pins,
    }
    if maturity is not None:
        result["maturity"] = maturity
    return result


def dump_frontmatter(fm: dict[str, Any]) -> str:
    lines = [
        "---",
        f"doc_type: {fm['doc_type']}",
        f'track: "{fm["track"]}"',
    ]
    rev = fm["doc_rev"]
    if is_frozen_rev(rev):
        lines.append(f"doc_rev: {rev}")
    else:
        lines.append('doc_rev: "?"')
    maturity = fm.get("maturity")
    if isinstance(maturity, str) and maturity in MATURITY_VALUES:
        lines.append(f"maturity: {maturity}")
    pins = fm.get("pins") if isinstance(fm.get("pins"), dict) else {}
    if not pins:
        lines.append("pins: {}")
    else:
        pin_yaml = yaml.safe_dump(
            {"pins": pins}, sort_keys=False, allow_unicode=True
        ).rstrip()
        lines.append(pin_yaml)
    lines.append(f"created: {fm['created']}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def _normalize_md(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def ensure_doc_frontmatter(
    text: str, stem: str, status: dict[str, Any] | None
) -> tuple[str, str]:
    old_fm, body = split_frontmatter(text)
    had_stub = any(key in old_fm for key in STUB_FRONTMATTER_KEYS)
    missing_required = any(key not in old_fm for key in FRONTMATTER_KEYS)
    built = _frontmatter_for_doc(stem, status)
    new_fm = {**built, "created": _preserve_created(old_fm.get("created"))}
    old_maturity = old_fm.get("maturity")
    if (
        "maturity" not in new_fm
        and isinstance(old_maturity, str)
        and old_maturity in MATURITY_VALUES
    ):
        new_fm["maturity"] = old_maturity
    new_text = dump_frontmatter(new_fm) + body
    new_text = _normalize_md(new_text)
    if new_text == _normalize_md(text):
        return new_text, "ok"
    aligned = False
    for key in FRONTMATTER_KEYS:
        if key == "created":
            continue
        if key in old_fm and old_fm[key] != new_fm[key]:
            aligned = True
            break
    if had_stub or aligned:
        return new_text, "fixed"
    if missing_required:
        return new_text, "created"
    return new_text, "fixed"


def has_cascade_docs(
    planning_dir: Path, *, stems: tuple[str, ...] | None = None
) -> bool:
    allowed = stems if stems is not None else stems_for_dir(planning_dir)
    check = (*allowed, *LEGACY_DOC_STEMS.keys())
    return any(
        (planning_dir / f"{stem}.md").is_file()
        or (planning_dir / f"{stem}.yaml").is_file()
        for stem in check
    )


def default_unfrozen_status(
    injection_version: int, *, stems: tuple[str, ...] | None = None
) -> dict[str, Any]:
    level_stems = stems if stems is not None else DOC_STEMS
    levels: dict[str, Any] = {
        doc: {"rev": "?", "digest": None, "pins": {}} for doc in level_stems
    }
    data: dict[str, Any] = {
        "claude_config_version": injection_version,
        "track": "0.1",
        "product": _UNFROZEN_REV,
        "docs": _UNFROZEN_REV,
        "next": None,
        "docs_shipped": False,
        "product_status": "?",
        "levels": levels,
        "next_levels": {},
        "challenge": {},
        "next_challenge": {},
    }
    data["mint_hash"] = compute_mint_hash(data)
    return data


def _fill_status_payload(data: dict[str, Any], defaults: dict[str, Any]) -> bool:
    payload_changed = False
    payload_keys = (
        "track",
        "product",
        "docs",
        "next",
        "docs_shipped",
        "next_levels",
    )
    for key in payload_keys:
        if key not in data:
            data[key] = defaults[key]
            payload_changed = True
    return payload_changed


def _fill_status_levels(data: dict[str, Any], defaults: dict[str, Any]) -> bool:
    payload_changed = False
    if "levels" not in data or not isinstance(data["levels"], dict):
        data["levels"] = defaults["levels"]
        return True
    for doc, row in defaults["levels"].items():
        existing = data["levels"].get(doc)
        if not isinstance(existing, dict):
            data["levels"][doc] = dict(row)
            payload_changed = True
            continue
        for field_name, default_val in row.items():
            if field_name not in existing:
                existing[field_name] = default_val
                payload_changed = True
    return payload_changed


def fill_status_missing(
    data: dict[str, Any],
    injection_version: int,
    *,
    stems: tuple[str, ...] | None = None,
) -> tuple[bool, bool]:
    payload_changed = False
    meta_changed = False
    defaults = default_unfrozen_status(injection_version, stems=stems)
    payload_changed |= _fill_status_payload(data, defaults)
    if "product_status" not in data:
        data["product_status"] = defaults["product_status"]
        meta_changed = True
    for key in CHALLENGE_KEYS:
        if key not in data or not isinstance(data.get(key), dict):
            data[key] = {}
            meta_changed = True
    payload_changed |= _fill_status_levels(data, defaults)
    if data.get("claude_config_version") != injection_version:
        data["claude_config_version"] = injection_version
        meta_changed = True
    return payload_changed, meta_changed


def fill_rrr_status_missing(data: dict[str, Any], injection_version: int) -> bool:
    defaults = default_rrr_status(injection_version)
    changed = False
    for key, value in defaults.items():
        if key not in data:
            data[key] = value
            changed = True
    if data.get("claude_config_version") != injection_version:
        data["claude_config_version"] = injection_version
        changed = True
    return changed


def load_doc_frontmatter(
    planning_dir: Path, *, stems: tuple[str, ...] | None = None
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for doc in stems if stems is not None else stems_for_dir(planning_dir):
        path = planning_dir / f"{doc}.md"
        if path.is_file():
            result[doc] = parse_frontmatter(path.read_text(encoding="utf-8"))
    return result


def is_frozen_rev(rev: Any) -> bool:
    return isinstance(rev, int) and not isinstance(rev, bool) and rev >= 1


def is_open_rev(rev: Any) -> bool:
    return rev == "?" or rev is None


def compute_doc_digest(items: list[Item], doc: str) -> str:
    records = [item.to_record() for item in items if item.doc == doc]
    records.sort(key=lambda row: str(row.get("id", "")))
    payload = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _canonical_pins(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {}
    pins: dict[str, Any] = {}
    for name, pin in raw.items():
        if isinstance(pin, dict):
            pins[str(name)] = {"digest": pin.get("digest"), "rev": pin.get("rev")}
        else:
            pins[str(name)] = pin
    return pins


def _canonical_level(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {}
    return {
        "digest": raw.get("digest"),
        "pins": _canonical_pins(raw.get("pins")),
        "rev": raw.get("rev"),
    }


def _canonical_levels(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {}
    return {str(name): _canonical_level(value) for name, value in raw.items()}


def canonical_mint_payload(status: dict[str, Any]) -> dict[str, Any]:
    # MINT_EXCLUDED_KEYS (claude_config_version, product_status, challenge,
    # next_challenge, mint_hash) stay out — unknown top-level keys are ignored.
    return {
        "docs": str(status.get("docs", "")),
        "docs_shipped": bool(status.get("docs_shipped", False)),
        "levels": _canonical_levels(status.get("levels")),
        "next": status.get("next"),
        "next_levels": _canonical_levels(status.get("next_levels")),
        "product": str(status.get("product", "")),
        "track": str(status.get("track", "")),
    }


def compute_mint_hash(status: dict[str, Any]) -> str:
    payload = json.dumps(
        canonical_mint_payload(status),
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _challenge_key(*, next_track: bool) -> str:
    return "next_challenge" if next_track else "challenge"


def _status_levels_key(*, next_track: bool) -> str:
    return "next_levels" if next_track else "levels"


def challenge_map(
    status: dict[str, Any], *, next_track: bool = False
) -> dict[str, Any]:
    key = _challenge_key(next_track=next_track)
    raw = status.get(key)
    if not isinstance(raw, dict):
        empty: dict[str, Any] = {}
        status[key] = empty
        return empty
    return raw


def challenge_doc_stem(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    token = value.strip().split()[0]
    if token.endswith(".md"):
        token = token[:-3]
    canonical = canonicalize_doc_stem(token)
    if canonical in DOC_STEMS:
        return canonical
    return None


def _live_digest(status: dict[str, Any], doc: str, *, next_track: bool) -> str | None:
    levels = status.get(_status_levels_key(next_track=next_track))
    if not isinstance(levels, dict):
        return None
    row = levels.get(doc)
    if not isinstance(row, dict):
        return None
    digest = row.get("digest")
    return digest if isinstance(digest, str) else None


def invalidate_challenge_on_compose(
    status: dict[str, Any],
    doc: str,
    *,
    next_track: bool = False,
) -> None:
    if doc not in DOC_STEMS:
        return
    row = challenge_map(status, next_track=next_track).get(doc)
    if not isinstance(row, dict):
        return
    if row.get("status") in {"clean", "dirty-accepted"}:
        row["status"] = "dirty"


def invalidate_challenge_on_digest_change(
    status: dict[str, Any],
    *,
    next_track: bool = False,
) -> None:
    challenge = challenge_map(status, next_track=next_track)
    for doc, row in challenge.items():
        if doc not in DOC_STEMS or not isinstance(row, dict):
            continue
        if _live_digest(status, doc, next_track=next_track) != row.get(
            "scanned_digest"
        ):
            row["status"] = "dirty"


def _collect_dirty_stems(findings: list[Any]) -> set[str]:
    dirty_stems: set[str] = set()
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        stem = challenge_doc_stem(finding.get("doc"))
        if stem is None:
            stem = challenge_doc_stem(finding.get("doc_ref"))
        if stem is not None:
            dirty_stems.add(stem)
    return dirty_stems


def _collect_scanned_stems(
    docs_reviewed: list[Any] | None, dirty_stems: set[str]
) -> set[str]:
    scanned: set[str] = set()
    if docs_reviewed:
        for name in docs_reviewed:
            stem = challenge_doc_stem(name)
            if stem is not None:
                scanned.add(stem)
    if not scanned:
        scanned = set(dirty_stems)
    return scanned


def stamp_challenge_status(
    status: dict[str, Any],
    findings: list[Any],
    docs_reviewed: list[Any] | None = None,
    *,
    next_track: bool = False,
) -> None:
    challenge = challenge_map(status, next_track=next_track)
    dirty_stems = _collect_dirty_stems(findings)
    scanned = _collect_scanned_stems(docs_reviewed, dirty_stems)
    for doc in scanned:
        challenge[doc] = {
            "status": "dirty" if doc in dirty_stems else "clean",
            "scanned_digest": _live_digest(status, doc, next_track=next_track),
        }


def accept_challenge_residual(
    status: dict[str, Any],
    docs: list[str],
    *,
    next_track: bool = False,
) -> None:
    challenge = challenge_map(status, next_track=next_track)
    for doc in docs:
        if doc not in DOC_STEMS:
            continue
        row = challenge.get(doc)
        if not isinstance(row, dict):
            row = {"scanned_digest": None}
            challenge[doc] = row
        row["status"] = "dirty-accepted"
        digest = _live_digest(status, doc, next_track=next_track)
        if digest is not None:
            row["scanned_digest"] = digest
        elif "scanned_digest" not in row:
            row["scanned_digest"] = None


def _levels_for_dir(status: dict[str, Any], planning_dir: Path) -> dict[str, Any]:
    nxt = status.get("next")
    if (
        TRACK_DIR_RE.fullmatch(planning_dir.name)
        and nxt is not None
        and planning_dir.name == str(nxt)
    ):
        raw = status.get("next_levels") or {}
    else:
        raw = status.get("levels") or {}
    return raw if isinstance(raw, dict) else {}


def _load_frozen_levels(planning_dir: Path) -> list[str] | None:
    path = planning_dir / "session-state.json"
    if not path.is_file() and TRACK_DIR_RE.fullmatch(planning_dir.name):
        path = planning_dir.parent / "session-state.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    frozen = payload.get("frozen_levels")
    if not isinstance(frozen, list):
        return None
    return [str(item) for item in frozen]


def _check_frozen_rev_state(
    doc: str, rev: Any, frozen_levels: list[str] | None
) -> list[Issue]:
    if is_frozen_rev(rev) and frozen_levels is not None and doc not in frozen_levels:
        return [
            Issue.error(
                "REV_WHILE_OPEN",
                f"{doc} has integer rev {rev} but is not in frozen_levels",
                doc,
            )
        ]
    return []


def _check_frontmatter_rev(
    doc: str, frontmatter: dict[str, dict[str, Any]], rev: Any
) -> list[Issue]:
    fm_rev = frontmatter.get(doc, {}).get("doc_rev")
    if is_frozen_rev(fm_rev) and is_open_rev(rev):
        return [
            Issue.error(
                "REV_WHILE_OPEN",
                f"{doc} frontmatter doc_rev is integer while status " "rev is unfrozen",
                doc,
            )
        ]
    return []


def _check_maturity(
    doc: str,
    levels: dict[str, Any],
    frontmatter: dict[str, dict[str, Any]],
    rev: Any,
) -> list[Issue]:
    """Validate optional doc maturity; refuse freeze while code-extraction."""
    issues: list[Issue] = []
    raw = levels.get(doc)
    row = raw if isinstance(raw, dict) else {}
    status_mat = row.get("maturity")
    fm_mat = frontmatter.get(doc, {}).get("maturity")
    for label, value in (("status", status_mat), ("frontmatter", fm_mat)):
        if value is None:
            continue
        if not isinstance(value, str) or value not in MATURITY_VALUES:
            issues.append(
                Issue.error(
                    "INVALID_MATURITY",
                    f"{doc} {label} maturity {value!r} not in "
                    f"{sorted(MATURITY_VALUES)}",
                    doc,
                )
            )
    effective = fm_mat if fm_mat is not None else status_mat
    if effective == "code-extraction" and is_frozen_rev(rev):
        issues.append(
            Issue.error(
                "CODE_EXTRACTION_FROZEN",
                f"{doc} maturity is code-extraction — freeze/rev mint blocked",
                doc,
            )
        )
    fm_rev = frontmatter.get(doc, {}).get("doc_rev")
    if effective == "code-extraction" and is_frozen_rev(fm_rev):
        issues.append(
            Issue.error(
                "CODE_EXTRACTION_FROZEN",
                f"{doc} frontmatter doc_rev frozen while maturity is "
                "code-extraction",
                doc,
            )
        )
    return issues


def _load_parent_items(planning_dir: Path, parent: str) -> list[Item]:
    """Items for parent digest — local dir first, else discovery sibling items.json."""
    local_md = planning_dir / f"{parent}.md"
    if local_md.is_file():
        from .parse import parse_markdown

        items, _ = parse_markdown(
            local_md.read_text(encoding="utf-8"), local_md.name, migrate=True
        )
        return items
    discovery = discovery_dir_for(planning_dir)
    if discovery is None:
        return []
    items_path = discovery / "items.json"
    if not items_path.is_file():
        discovery_md = discovery / f"{parent}.md"
        if discovery_md.is_file():
            from .parse import parse_markdown

            items, _ = parse_markdown(
                discovery_md.read_text(encoding="utf-8"),
                discovery_md.name,
                migrate=True,
            )
            return items
        return []
    try:
        payload = json.loads(items_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, dict):
        return []
    raw_items = payload.get("items")
    if not isinstance(raw_items, list):
        return []
    result: list[Item] = []
    for row in raw_items:
        if not isinstance(row, dict) or row.get("doc") != parent:
            continue
        item_id = row.get("id")
        if not isinstance(item_id, str):
            continue
        prefix = item_id.split("-", 1)[0]
        result.append(
            Item(
                id=item_id,
                title=str(row.get("title", "")),
                prefix=prefix,
                doc=parent,
                parent=row.get("parent"),
                kind=str(row.get("kind", "leaf")),
                spec=str(row.get("spec", "draft")),
                status=row.get("status"),
                priority=row.get("priority"),
                tag=row.get("tag"),
                goal_type=row.get("goal_type"),
                reach=row.get("reach"),
                impact=row.get("impact"),
                confidence=row.get("confidence"),
                effort=row.get("effort"),
                moscow=row.get("moscow"),
                kano=row.get("kano"),
                supersedes=row.get("supersedes"),
                superseded_by=row.get("superseded_by"),
                rationale=row.get("rationale"),
                source_file=str(items_path),
                raw_keys=set(),
                raw_meta={},
            )
        )
    return result


def _merged_levels_for_pins(
    planning_dir: Path, levels: dict[str, Any]
) -> dict[str, Any]:
    """Merge discovery status levels when Plan pins against BRD across dirs."""
    merged = dict(levels)
    parent_missing = [
        parent
        for doc, parent in PARENT_DOC.items()
        if doc in stems_for_dir(planning_dir) and parent not in merged
    ]
    if not parent_missing:
        return merged
    discovery = discovery_dir_for(planning_dir)
    if discovery is None or discovery == phase_root(planning_dir):
        return merged
    status_path = find_phase_status_path(discovery)
    if status_path is None:
        return merged
    status, _ = load_status(status_path)
    if status is None:
        return merged
    parent_levels = _levels_for_dir(status, discovery)
    for name, row in parent_levels.items():
        if name not in merged:
            merged[name] = row
    return merged


def _check_parent_pin(
    doc: str,
    rev: Any,
    row: dict[str, Any],
    levels: dict[str, Any],
    items: list[Item],
    planning_dir: Path,
) -> list[Issue]:
    parent = PARENT_DOC.get(doc)
    if parent is None or not is_frozen_rev(rev):
        return []
    parent_row = levels.get(parent)
    parent_rev = parent_row.get("rev") if isinstance(parent_row, dict) else None
    if is_open_rev(parent_rev) or parent_rev is None:
        return [
            Issue.error(
                "PARENT_UNFROZEN",
                f"frozen {doc} but parent {parent} is still unfrozen",
                doc,
            )
        ]
    parent_items = [item for item in items if item.doc == parent]
    if not parent_items:
        parent_items = _load_parent_items(planning_dir, parent)
    live_digest = compute_doc_digest(parent_items, parent)
    pins = row.get("pins") if isinstance(row.get("pins"), dict) else {}
    pin = pins.get(parent) if isinstance(pins, dict) else None
    pin_digest = pin.get("digest") if isinstance(pin, dict) else None
    pin_rev = pin.get("rev") if isinstance(pin, dict) else None
    if pin_digest != live_digest or pin_rev != parent_rev:
        return [
            Issue.error(
                "STALE_PIN",
                f"{doc} pin for {parent} does not match parent rev/digest",
                doc,
            )
        ]
    return []


def _check_doc_baseline(
    doc: str,
    levels: dict[str, Any],
    frozen_levels: list[str] | None,
    frontmatter: dict[str, dict[str, Any]],
    items: list[Item],
    planning_dir: Path,
) -> list[Issue]:
    issues: list[Issue] = []
    raw = levels.get(doc)
    row = raw if isinstance(raw, dict) else {}
    rev = row.get("rev")
    issues.extend(_check_frozen_rev_state(doc, rev, frozen_levels))
    issues.extend(_check_frontmatter_rev(doc, frontmatter, rev))
    issues.extend(_check_maturity(doc, levels, frontmatter, rev))
    issues.extend(_check_parent_pin(doc, rev, row, levels, items, planning_dir))
    return issues


def check_baselines(planning_dir: Path, items: list[Item]) -> list[Issue]:
    status_path = find_status_path(planning_dir)
    if status_path is None:
        return []
    status, issues = load_status(status_path)
    if status is None:
        return issues
    expected = compute_mint_hash(status)
    recorded = status.get("mint_hash")
    if recorded != expected:
        issues.append(
            Issue.error(
                "HAND_BUMP",
                "frozen rev/pins/track changed without skill mint_hash",
            )
        )
    levels = _merged_levels_for_pins(
        planning_dir, _levels_for_dir(status, planning_dir)
    )
    frozen_levels = _load_frozen_levels(planning_dir)
    frontmatter = load_doc_frontmatter(planning_dir)
    for doc in stems_for_dir(planning_dir):
        issues.extend(
            _check_doc_baseline(
                doc, levels, frozen_levels, frontmatter, items, planning_dir
            )
        )
    return issues


def check_business_case(planning_dir: Path) -> list[Issue]:
    """Validate business-case.yaml shape when the file is present."""
    path = planning_dir / BUSINESS_CASE_NAME
    if not path.is_file():
        discovery = discovery_dir_for(planning_dir)
        if discovery is not None:
            path = discovery / BUSINESS_CASE_NAME
    if not path.is_file():
        return [
            Issue.error(
                "MISSING_BUSINESS_CASE",
                f"{BUSINESS_CASE_NAME} is required",
            )
        ]
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [
            Issue.error(
                "BUSINESS_CASE_PARSE",
                f"{BUSINESS_CASE_NAME} is not valid YAML: {exc}",
            )
        ]
    if not isinstance(payload, dict):
        return [
            Issue.error(
                "BUSINESS_CASE_SHAPE",
                f"{BUSINESS_CASE_NAME} must be a mapping",
            )
        ]
    issues: list[Issue] = []
    missing = sorted(BUSINESS_CASE_REQUIRED_FIELDS - set(payload))
    if missing:
        issues.append(
            Issue.error(
                "BUSINESS_CASE_FIELDS",
                f"{BUSINESS_CASE_NAME} missing required fields: {', '.join(missing)}",
            )
        )
    for key in ("vision", "problem", "north_star", "viability_verdict"):
        value = payload.get(key)
        if key in payload and (
            value is None or (isinstance(value, str) and not value.strip())
        ):
            issues.append(
                Issue.error(
                    "BUSINESS_CASE_EMPTY",
                    f"{BUSINESS_CASE_NAME} field '{key}' must be non-empty",
                    key,
                )
            )
    return issues


def _check_execute_slice_empty_fields(payload: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    for key in ("why", "success_signal", "slice_id"):
        value = payload.get(key)
        if key in payload and (
            value is None or (isinstance(value, str) and not value.strip())
        ):
            issues.append(
                Issue.error(
                    "EXECUTE_SLICE_EMPTY",
                    f"{EXECUTE_SLICE_NAME} field '{key}' must be non-empty",
                    key,
                )
            )
    return issues


def _check_execute_slice_delta_paths(
    delta_paths: list[Any], planning_dir: Path
) -> list[Issue]:
    issues: list[Issue] = []
    plan_root = planning_dir.resolve()
    for raw in delta_paths:
        if not isinstance(raw, str) or not raw.strip():
            issues.append(
                Issue.error(
                    "EXECUTE_SLICE_DELTA_PATH",
                    f"{EXECUTE_SLICE_NAME} {_PINS_DELTA_PATHS} "
                    "entry must be a non-empty string",
                    _PINS_DELTA_PATHS,
                )
            )
            continue
        rel = Path(raw)
        if rel.is_absolute() or ".." in rel.parts:
            issues.append(
                Issue.error(
                    "EXECUTE_SLICE_DELTA_PATH",
                    f"{EXECUTE_SLICE_NAME} delta path must be "
                    f"relative under plan dir: {raw}",
                    raw,
                )
            )
            continue
        candidate = (planning_dir / rel).resolve()
        if not candidate.is_relative_to(plan_root):
            issues.append(
                Issue.error(
                    "EXECUTE_SLICE_DELTA_PATH",
                    f"{EXECUTE_SLICE_NAME} delta path escapes plan dir: {raw}",
                    raw,
                )
            )
        elif not candidate.is_file():
            issues.append(
                Issue.error(
                    "EXECUTE_SLICE_DELTA_PATH",
                    f"{EXECUTE_SLICE_NAME} delta path does not exist: {raw}",
                    raw,
                )
            )
    return issues


def _check_execute_slice_pins(
    pins: Any, planning_dir: Path, *, pins_present: bool
) -> list[Issue]:
    if pins_present and not isinstance(pins, dict):
        return [
            Issue.error(
                "EXECUTE_SLICE_PINS",
                f"{EXECUTE_SLICE_NAME} pins must be a mapping",
                "pins",
            )
        ]
    if not isinstance(pins, dict):
        return []
    issues: list[Issue] = []
    delta_paths = pins.get("delta_paths")
    if delta_paths is None:
        issues.append(
            Issue.error(
                "EXECUTE_SLICE_PINS",
                f"{EXECUTE_SLICE_NAME} {_PINS_DELTA_PATHS} is required",
                _PINS_DELTA_PATHS,
            )
        )
    elif not isinstance(delta_paths, list):
        issues.append(
            Issue.error(
                "EXECUTE_SLICE_PINS",
                f"{EXECUTE_SLICE_NAME} {_PINS_DELTA_PATHS} must be a list",
                _PINS_DELTA_PATHS,
            )
        )
    else:
        issues.extend(_check_execute_slice_delta_paths(delta_paths, planning_dir))
    return issues


def check_execute_slice(planning_dir: Path) -> list[Issue]:
    """Validate execute-slice.yaml when present (required fields + delta_paths exist).

    Absent file is OK — not every plan dir has a frozen slice. Judgment owns
    smell/WWAS; static owns hollow/broken kernel paths only.
    """
    path = planning_dir / EXECUTE_SLICE_NAME
    if not path.is_file():
        return []
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [
            Issue.error(
                "EXECUTE_SLICE_PARSE",
                f"{EXECUTE_SLICE_NAME} is not valid YAML: {exc}",
            )
        ]
    if not isinstance(payload, dict):
        return [
            Issue.error(
                "EXECUTE_SLICE_SHAPE",
                f"{EXECUTE_SLICE_NAME} must be a mapping",
            )
        ]
    issues: list[Issue] = []
    missing = sorted(EXECUTE_SLICE_REQUIRED_FIELDS - set(payload))
    if missing:
        issues.append(
            Issue.error(
                "EXECUTE_SLICE_FIELDS",
                f"{EXECUTE_SLICE_NAME} missing required fields: {', '.join(missing)}",
            )
        )
    issues.extend(_check_execute_slice_empty_fields(payload))
    pins_issues = _check_execute_slice_pins(
        payload.get("pins"), planning_dir, pins_present="pins" in payload
    )
    issues.extend(pins_issues)
    return issues


def _discovery_brd_frozen(discovery: Path) -> bool:
    status_path = find_phase_status_path(discovery)
    if status_path is None:
        return False
    status, _ = load_status(status_path)
    if status is None:
        return False
    levels = _levels_for_dir(status, discovery)
    brd_row = levels.get("brd")
    return isinstance(brd_row, dict) and is_frozen_rev(brd_row.get("rev"))


def check_plan_entry(planning_dir: Path) -> list[Issue]:
    """Plan entry gate: frozen BRD + valid business-case.yaml.

    Call when composing/changing PRD or when validating a dir that already
    has ``prd.md``. Discovery-only dirs (ES+MRD+BRD, no PRD) skip this.
    Looks in ``docs/discovery/`` when ``planning_dir`` is ``docs/plan/``.
    """
    issues: list[Issue] = []
    frozen = _load_frozen_levels(planning_dir)
    discovery = discovery_dir_for(planning_dir)
    if frozen is None and discovery is not None:
        frozen = _load_frozen_levels(discovery)
    brd_ok = frozen is not None and "brd" in frozen
    if not brd_ok and discovery is not None:
        brd_ok = _discovery_brd_frozen(discovery)
    if not brd_ok:
        issues.append(
            Issue.error(
                "PLAN_ENTRY_BRD",
                "Plan entry requires brd in session_state.frozen_levels "
                "(run rr-discovery freeze first)",
            )
        )
    issues.extend(check_business_case(planning_dir))
    return issues


def has_prd_doc(planning_dir: Path) -> bool:
    return (planning_dir / "prd.md").is_file() or (planning_dir / "prd.yaml").is_file()
