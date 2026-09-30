"""Composite drift signals for Stop inject (high bar)."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

from .constants import (
    BASH_DISCOVERY_RE,
    BASH_INFO_MIN,
    CORRECTION_RE,
    EXPLORE_TOOLS,
    EXPLORE_TOOLS_LOWER,
    EXTREME_REREAD,
    EXTREME_THRASH,
    REREAD_MIN,
    SHELL_TOOLS,
    THRASH_MIN,
    THRASH_WINDOW,
    TOOL_READ,
    WRITE_TOOLS,
)
from .redact import redact_secrets


@dataclass(frozen=True)
class SignalHit:
    class_id: str
    evidence: str
    extreme: bool = False


def _tool_name(event: dict[str, Any]) -> str:
    return str(event.get("tool") or event.get("tool_name") or "").strip()


def _path_or_cmd(event: dict[str, Any]) -> str:
    return str(event.get("fingerprint") or event.get("path") or event.get("cmd") or "")


def _explore_streak(events: list[dict[str, Any]]) -> int:
    """Longest consecutive explore-tool streak with no Write/Edit."""
    streak = 0
    max_streak = 0
    for ev in events:
        name = _tool_name(ev)
        if name in WRITE_TOOLS:
            streak = 0
            continue
        if name in EXPLORE_TOOLS or name.lower() in EXPLORE_TOOLS_LOWER:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            # Unknown tools break the thrash streak (conservative).
            streak = 0
    return max_streak


def _tail_explore_streak(events: list[dict[str, Any]]) -> int:
    """Explore-tool streak at the end of the event list (newest first)."""
    full_streak = 0
    for ev in reversed(events):
        name = _tool_name(ev)
        if name in WRITE_TOOLS:
            break
        if name in EXPLORE_TOOLS:
            full_streak += 1
        else:
            break
    return full_streak


def score_tool_thrash(events: list[dict[str, Any]]) -> SignalHit | None:
    """≥K consecutive explore tools with no Write/Edit in a sliding window."""
    if not events:
        return None
    best = max(
        _explore_streak(events[-THRASH_WINDOW:]),
        _tail_explore_streak(events),
    )
    if best >= EXTREME_THRASH:
        return SignalHit(
            "tool_thrash",
            f"{best} consecutive explore tools with no write",
            extreme=True,
        )
    if best >= THRASH_MIN:
        return SignalHit(
            "tool_thrash",
            f"{best} consecutive explore tools with no write",
        )
    return None


def score_reread(events: list[dict[str, Any]]) -> SignalHit | None:
    """Same path Read ≥M times."""
    counts: Counter[str] = Counter()
    for ev in events:
        if _tool_name(ev) != TOOL_READ:
            continue
        path = _path_or_cmd(ev)
        if path:
            counts[path] += 1
    if not counts:
        return None
    path, n = counts.most_common(1)[0]
    if n >= EXTREME_REREAD:
        return SignalHit("reread", f"Read {path} x{n}", extreme=True)
    if n >= REREAD_MIN:
        return SignalHit("reread", f"Read {path} x{n}")
    return None


def score_tool_fail_retry(events: list[dict[str, Any]]) -> SignalHit | None:
    """postToolUseFailure then same tool fingerprint retry."""
    for i, ev in enumerate(events):
        if not ev.get("failed"):
            continue
        fp = (_tool_name(ev), _path_or_cmd(ev))
        if not fp[0]:
            continue
        for later in events[i + 1 :]:
            if later.get("failed"):
                continue
            if (_tool_name(later), _path_or_cmd(later)) == fp:
                return SignalHit(
                    "tool_fail_retry",
                    f"{fp[0]} failed then retried ({fp[1] or 'no-path'})",
                )
    return None


def score_bash_info_loop(
    events: list[dict[str, Any]],
    *,
    skill_bound: bool,
) -> SignalHit | None:
    """Bash discovery fingerprints after skill already bound."""
    if not skill_bound:
        return None
    hits = 0
    sample = ""
    for ev in events:
        name = _tool_name(ev)
        if name not in SHELL_TOOLS:
            continue
        cmd = _path_or_cmd(ev)
        if BASH_DISCOVERY_RE.search(cmd or ""):
            hits += 1
            if not sample:
                sample = redact_secrets(cmd or "")[:80]
    if hits >= BASH_INFO_MIN:
        return SignalHit(
            "bash_info_loop",
            f"{hits} discovery Bash after skill bound ({sample})",
        )
    return None


def score_correction(
    events: list[dict[str, Any]],
    last_user_text: str | None,
) -> SignalHit | None:
    """Correction lexicon on last user turn AND prior thrash."""
    if not last_user_text:
        return None
    match = CORRECTION_RE.search(last_user_text)
    if not match:
        return None
    thrash = score_tool_thrash(events)
    if thrash is None:
        # Soft thrash: any ≥THRASH_MIN/2 explore streak still counts with correction.
        explore = sum(
            1 for ev in events[-THRASH_WINDOW:] if _tool_name(ev) in EXPLORE_TOOLS
        )
        if explore < max(3, THRASH_MIN // 2):
            return None
    snippet = redact_secrets(match.group(0))[:40]
    return SignalHit("correction", f"user correction '{snippet}' with prior thrash")


_SCORERS = (
    score_tool_thrash,
    score_reread,
    score_tool_fail_retry,
)


def score_events(
    events: list[dict[str, Any]],
    *,
    skill_bound: bool,
    last_user_text: str | None = None,
) -> list[SignalHit]:
    """Return distinct signal hits that fire."""
    hits: list[SignalHit] = []
    for fn in _SCORERS:
        hit = fn(events)
        if hit is not None:
            hits.append(hit)
    bash = score_bash_info_loop(events, skill_bound=skill_bound)
    if bash is not None:
        hits.append(bash)
    corr = score_correction(events, last_user_text)
    if corr is not None:
        hits.append(corr)
    # Dedupe by class_id keeping extreme preferred.
    by_id: dict[str, SignalHit] = {}
    for h in hits:
        prev = by_id.get(h.class_id)
        if prev is None or (h.extreme and not prev.extreme):
            by_id[h.class_id] = h
    return list(by_id.values())


def meets_inject_bar(hits: list[SignalHit]) -> bool:
    """Require ≥2 distinct classes, or one class at extreme severity."""
    if any(h.extreme for h in hits):
        return True
    return len({h.class_id for h in hits}) >= 2


def fingerprint_cmd(cmd: str, *, max_len: int = 120) -> str:
    """Lean command fingerprint (not full stdout); secrets scrubbed first."""
    compact = re.sub(r"\s+", " ", redact_secrets(cmd or "").strip())
    return compact[:max_len]
