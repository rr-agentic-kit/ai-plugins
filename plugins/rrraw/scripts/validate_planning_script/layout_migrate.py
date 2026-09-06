"""Idempotent migrate of legacy docs layouts into ``docs/rr/{track}/{phase}/``."""

from __future__ import annotations

import contextlib
import shutil
from pathlib import Path

from .constants import (
    DISCOVERY_DIR,
    DISCOVERY_STEMS,
    LEGACY_DOC_STEMS,
    LEGACY_PLANNING_DIR,
    LEGACY_PLANS_DIR,
    PARKING_NAMES,
    PHASE_DIRS,
    PLAN_DIR,
    PLAN_STANDING_NAMES,
    PLAN_STEMS,
    STATUS_NAME,
    TRACK_DIR_RE,
    canonicalize_doc_stem,
)
from .rewrite import rewrite_planning_dir
from .workspace import (
    find_rrr_status_path,
    load_status,
    rr_root,
    rrr_status_path,
    track_phase_dir,
)


def _track_from_status_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    data, _ = load_status(path)
    if data is None:
        return None
    raw = data.get("track")
    if raw is not None and str(raw).strip():
        return str(raw).strip()
    return None


def resolve_migrate_track(docs: Path) -> str:
    """Track for migration: rrr-status → discovery status → plan status → ``0.1``."""
    for path in (
        find_rrr_status_path(docs),
        docs / DISCOVERY_DIR / STATUS_NAME,
        docs / PLAN_DIR / STATUS_NAME,
        docs / LEGACY_PLANS_DIR / STATUS_NAME,
        docs / LEGACY_PLANNING_DIR / STATUS_NAME,
    ):
        if path is None:
            continue
        track = _track_from_status_file(path)
        if track is not None:
            return track
    return "0.1"


def _is_migrated(docs: Path) -> bool:
    rr = rr_root(docs)
    if not rr.is_dir():
        return False
    if rrr_status_path(docs).is_file():
        return True
    for child in rr.iterdir():
        if not child.is_dir() or not TRACK_DIR_RE.fullmatch(child.name):
            continue
        if any((child / phase).is_dir() for phase in PHASE_DIRS):
            return True
    return False


def _has_phase_first(docs: Path) -> bool:
    return any((docs / phase).is_dir() for phase in PHASE_DIRS)


def _legacy_flat_dir(docs: Path) -> Path | None:
    for name in (LEGACY_PLANS_DIR, LEGACY_PLANNING_DIR):
        path = docs / name
        if path.is_dir():
            return path
    return None


def _move_path(src: Path, dest: Path, moves: list[str]) -> None:
    if not src.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if src.is_dir() and dest.is_dir():
            for child in list(src.iterdir()):
                _move_path(child, dest / child.name, moves)
            with contextlib.suppress(OSError):
                src.rmdir()
            return
        return
    shutil.move(str(src), str(dest))
    moves.append(f"moved {src} → {dest}")


def _move_parking(docs: Path, moves: list[str]) -> None:
    parking = rr_root(docs)
    parking.mkdir(parents=True, exist_ok=True)
    for name in PARKING_NAMES:
        src = docs / name
        if src.is_file():
            _move_path(src, parking / name, moves)


def _move_phase_track_subdirs(phase_src: Path, phase: str, moves: list[str]) -> None:
    """``docs/{phase}/{next}/`` → ``docs/rr/{next}/{phase}/``."""
    if not phase_src.is_dir():
        return
    for child in list(phase_src.iterdir()):
        if child.is_dir() and TRACK_DIR_RE.fullmatch(child.name):
            dest = track_phase_dir(phase_src.parent, child.name, phase)
            _move_path(child, dest, moves)


def _move_phase_current(
    docs: Path, phase: str, track: str, moves: list[str]
) -> Path | None:
    """Move remaining ``docs/{phase}/`` contents into ``docs/rr/{track}/{phase}/``."""
    src = docs / phase
    if not src.is_dir():
        return None
    dest = track_phase_dir(docs, track, phase)
    dest.mkdir(parents=True, exist_ok=True)
    for child in list(src.iterdir()):
        _move_path(child, dest / child.name, moves)
    with contextlib.suppress(OSError):
        src.rmdir()
    return dest if dest.is_dir() else None


def _migrate_legacy_flat(
    docs: Path, flat: Path, track: str, moves: list[str]
) -> list[Path]:
    """Split ``docs/plans/`` (or ``planning/``) into versioned phase dirs."""
    discovery_dest = track_phase_dir(docs, track, DISCOVERY_DIR)
    plan_dest = track_phase_dir(docs, track, PLAN_DIR)
    discovery_dest.mkdir(parents=True, exist_ok=True)
    plan_dest.mkdir(parents=True, exist_ok=True)
    targets: list[Path] = []

    has_discovery_doc = any(
        (flat / f"{stem}.md").is_file() or (flat / f"{stem}.yaml").is_file()
        for stem in (*DISCOVERY_STEMS, *LEGACY_DOC_STEMS)
    )
    has_plan_doc = any(
        (flat / f"{stem}.md").is_file() or (flat / f"{stem}.yaml").is_file()
        for stem in PLAN_STEMS
    ) or any((flat / name).exists() for name in PLAN_STANDING_NAMES)

    shared = {
        "items.json",
        "session-state.json",
        "decision-ledger.yaml",
        "business-case.yaml",
        STATUS_NAME,
        "raw-history",
    }

    for child in list(flat.iterdir()):
        name = child.name
        if name in PARKING_NAMES:
            _move_path(child, rr_root(docs) / name, moves)
            continue
        if TRACK_DIR_RE.fullmatch(name) and child.is_dir():
            dest = track_phase_dir(docs, name, DISCOVERY_DIR)
            _move_path(child, dest, moves)
            targets.append(dest)
            continue
        if name in PLAN_STANDING_NAMES or name.startswith("architecture."):
            _move_path(child, plan_dest / name, moves)
            continue
        if name.endswith(".challenge.report.md"):
            report_stem = name[: -len(".challenge.report.md")]
            can = canonicalize_doc_stem(report_stem)
            dest_dir = (
                plan_dest
                if can in PLAN_STEMS or report_stem in {"architecture", "constitution"}
                else discovery_dest
            )
            _move_path(child, dest_dir / name, moves)
            continue
        if name.endswith(".notes.yaml"):
            note_stem = name[: -len(".notes.yaml")]
            can = canonicalize_doc_stem(note_stem)
            dest_dir = plan_dest if can in PLAN_STEMS else discovery_dest
            _move_path(child, dest_dir / name, moves)
            continue
        stem = child.stem if child.is_file() else name
        can = canonicalize_doc_stem(stem)
        if can in PLAN_STEMS:
            _move_path(child, plan_dest / name, moves)
            continue
        if can in DISCOVERY_STEMS or stem in LEGACY_DOC_STEMS:
            _move_path(child, discovery_dest / name, moves)
            continue
        if name in shared:
            dest_dir = (
                discovery_dest if has_discovery_doc or not has_plan_doc else plan_dest
            )
            _move_path(child, dest_dir / name, moves)
            continue
        _move_path(child, discovery_dest / name, moves)

    with contextlib.suppress(OSError):
        flat.rmdir()
    if discovery_dest.is_dir():
        targets.append(discovery_dest)
    if plan_dest.is_dir() and (
        has_plan_doc or any(plan_dest.iterdir()) or not has_discovery_doc
    ):
        targets.append(plan_dest)
    return targets


def migrate_docs_layout(docs: Path) -> tuple[str, str]:
    """Detect legacy layouts and move into ``docs/rr/``. Idempotent."""
    leftovers = _has_phase_first(docs) or _legacy_flat_dir(docs) is not None
    if _is_migrated(docs) and not leftovers:
        moves: list[str] = []
        _move_parking(docs, moves)
        if moves:
            return "fixed", "; ".join(moves)
        return "ok", "already migrated"

    moves = []
    targets: list[Path] = []
    track = resolve_migrate_track(docs)
    rr_root(docs).mkdir(parents=True, exist_ok=True)

    if _has_phase_first(docs):
        for phase in PHASE_DIRS:
            phase_src = docs / phase
            if not phase_src.is_dir():
                continue
            _move_phase_track_subdirs(phase_src, phase, moves)
            dest = _move_phase_current(docs, phase, track, moves)
            if dest is not None:
                targets.append(dest)
        _move_parking(docs, moves)
    else:
        flat = _legacy_flat_dir(docs)
        if flat is not None:
            targets.extend(_migrate_legacy_flat(docs, flat, track, moves))
            _move_parking(docs, moves)
        else:
            _move_parking(docs, moves)
            if not moves and _is_migrated(docs):
                return "ok", "already migrated"
            if not moves:
                return "ok", "nothing to migrate"

    for phase_dir in targets:
        if phase_dir.is_dir():
            rewrite_planning_dir(phase_dir, empty_ok=True)

    if not moves:
        return "ok", "already migrated"
    return "fixed", "; ".join(moves)
