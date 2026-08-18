"""status.yaml, frontmatter, mint hash, challenge, baselines."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from .constants import (
    CHALLENGE_KEYS,
    DOC_STEMS,
    FRONTMATTER_KEYS,
    FRONTMATTER_RE,
    PARENT_DOC,
    STATUS_NAME,
    STUB_FRONTMATTER_KEYS,
    TRACK_DIR_RE,
    matches_created_ts,
)
from .models import Issue, Item


def resolve_within_root(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    root_resolved = root.resolve()
    if not resolved.is_relative_to(root_resolved):
        raise ValueError(f"{path} is outside repo root {root}")
    return resolved


def plans_root(planning_dir: Path) -> Path:
    if (planning_dir / STATUS_NAME).is_file():
        return planning_dir
    if (
        TRACK_DIR_RE.fullmatch(planning_dir.name)
        and (planning_dir.parent / STATUS_NAME).is_file()
    ):
        return planning_dir.parent
    return planning_dir


def find_status_path(planning_dir: Path) -> Path | None:
    path = plans_root(planning_dir) / STATUS_NAME
    return path if path.is_file() else None


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


def _frontmatter_pins(
    stem: str, levels: dict[str, Any]
) -> dict[str, Any]:
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
    return {
        "doc_type": stem,
        "track": track,
        "doc_rev": rev,
        "pins": pins,
    }


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


def has_cascade_docs(planning_dir: Path) -> bool:
    return any(
        (planning_dir / f"{stem}.md").is_file()
        or (planning_dir / f"{stem}.yaml").is_file()
        for stem in DOC_STEMS
    )


def default_unfrozen_status(injection_version: int) -> dict[str, Any]:
    levels: dict[str, Any] = {
        doc: {"rev": "?", "digest": None, "pins": {}} for doc in DOC_STEMS
    }
    data: dict[str, Any] = {
        "claude_config_version": injection_version,
        "track": "0.1",
        "product": "0.1.0?",
        "docs": "0.1.0?",
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


def _fill_status_levels(
    data: dict[str, Any], defaults: dict[str, Any]
) -> bool:
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
    data: dict[str, Any], injection_version: int
) -> tuple[bool, bool]:
    payload_changed = False
    meta_changed = False
    defaults = default_unfrozen_status(injection_version)
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


def load_doc_frontmatter(planning_dir: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for doc in DOC_STEMS:
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
    if token in DOC_STEMS:
        return token
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


def _check_doc_baseline(
    doc: str,
    levels: dict[str, Any],
    frozen_levels: list[str] | None,
    frontmatter: dict[str, dict[str, Any]],
    items: list[Item],
) -> list[Issue]:
    issues: list[Issue] = []
    raw = levels.get(doc)
    row = raw if isinstance(raw, dict) else {}
    rev = row.get("rev")
    if is_frozen_rev(rev) and frozen_levels is not None and doc not in frozen_levels:
        issues.append(
            Issue.error(
                "REV_WHILE_OPEN",
                f"{doc} has integer rev {rev} but is not in frozen_levels",
                doc,
            )
        )
    fm_rev = frontmatter.get(doc, {}).get("doc_rev")
    if is_frozen_rev(fm_rev) and is_open_rev(rev):
        issues.append(
            Issue.error(
                "REV_WHILE_OPEN",
                f"{doc} frontmatter doc_rev is integer while status "
                "rev is unfrozen",
                doc,
            )
        )
    parent = PARENT_DOC.get(doc)
    if parent is None or not is_frozen_rev(rev):
        return issues
    parent_row = levels.get(parent)
    parent_rev = parent_row.get("rev") if isinstance(parent_row, dict) else None
    if is_open_rev(parent_rev) or parent_rev is None:
        issues.append(
            Issue.error(
                "PARENT_UNFROZEN",
                f"frozen {doc} but parent {parent} is still unfrozen",
                doc,
            )
        )
        return issues
    live_digest = compute_doc_digest(items, parent)
    pins = row.get("pins") if isinstance(row.get("pins"), dict) else {}
    pin = pins.get(parent) if isinstance(pins, dict) else None
    pin_digest = pin.get("digest") if isinstance(pin, dict) else None
    pin_rev = pin.get("rev") if isinstance(pin, dict) else None
    if pin_digest != live_digest or pin_rev != parent_rev:
        issues.append(
            Issue.error(
                "STALE_PIN",
                f"{doc} pin for {parent} does not match parent rev/digest",
                doc,
            )
        )
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
    levels = _levels_for_dir(status, planning_dir)
    frozen_levels = _load_frozen_levels(planning_dir)
    frontmatter = load_doc_frontmatter(planning_dir)
    for doc in DOC_STEMS:
        issues.extend(
            _check_doc_baseline(doc, levels, frozen_levels, frontmatter, items)
        )
    return issues
