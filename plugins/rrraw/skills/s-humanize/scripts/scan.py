from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_PATTERNS_PATH = Path(__file__).with_name("patterns.json")

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_TRANSITION_CLUSTER = re.compile(
    r"(?i)(?:^|[.!?]\s+)(Indeed|Furthermore|However|Notably|Additionally|"
    r"Consequently|Moreover|Therefore|Thus|Hence|Subsequently)\b"
)


def load_patterns() -> dict[str, list[dict[str, Any]]]:
    with _PATTERNS_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def _compile_flags(flags: str) -> int:
    value = 0
    if "i" in flags:
        value |= re.IGNORECASE
    return value


def _line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _match_entries(
    text: str,
    category: str,
    entries: list[dict[str, Any]],
    *,
    output_category: str | None = None,
) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    cat = output_category or category
    for entry in entries:
        pattern = re.compile(entry["pattern"], _compile_flags(entry.get("flags", "")))
        for match in pattern.finditer(text):
            hits.append(
                {
                    "category": cat,
                    "id": entry["id"],
                    "match": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "line": _line_number(text, match.start()),
                    "auto_fixable": bool(entry.get("auto_fixable", False)),
                    "needs_judgment": not bool(entry.get("auto_fixable", False)),
                }
            )
    return hits


def _sentence_stats(text: str) -> dict[str, Any]:
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text.strip()) if s.strip()]
    lengths = [len(s.split()) for s in sentences]
    em_dash_count = text.count("—") + text.count("–")
    avg = round(sum(lengths) / len(lengths), 1) if lengths else 0.0
    return {
        "sentence_count": len(sentences),
        "avg_sentence_length": avg,
        "em_dash_count": em_dash_count,
    }


def _transition_clusters(text: str) -> list[dict[str, Any]]:
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text.strip()) if s.strip()]
    hits: list[dict[str, Any]] = []
    cluster: list[tuple[int, str]] = []
    for idx, sentence in enumerate(sentences):
        if _TRANSITION_CLUSTER.search(sentence):
            cluster.append((idx, sentence))
        else:
            if len(cluster) >= 2:
                hits.append(
                    {
                        "category": "transition_cluster",
                        "id": "transition_cluster",
                        "match": " | ".join(s for _, s in cluster),
                        "sentence_indices": [i for i, _ in cluster],
                        "line": idx,
                        "auto_fixable": False,
                        "needs_judgment": True,
                    }
                )
            cluster = []
    if len(cluster) >= 2:
        hits.append(
            {
                "category": "transition_cluster",
                "id": "transition_cluster",
                "match": " | ".join(s for _, s in cluster),
                "sentence_indices": [i for i, _ in cluster],
                "line": cluster[0][0] + 1,
                "auto_fixable": False,
                "needs_judgment": True,
            }
        )
    return hits


def _em_dash_hits(count: int) -> list[dict[str, Any]]:
    if count < 2:
        return []
    return [
        {
            "category": "em_dash",
            "id": "em_dash_density",
            "match": f"{count} em/en dashes",
            "auto_fixable": False,
            "needs_judgment": True,
        }
    ]


def scan_text(text: str) -> dict[str, Any]:
    patterns = load_patterns()
    hits_by_category: dict[str, list[dict[str, Any]]] = {}

    for category in ("filler", "chatbot", "copula_avoidance", "banned_word", "not_x_but_y"):
        entries = patterns.get(category, [])
        if entries:
            hits_by_category[category] = _match_entries(text, category, entries)

    transition_hits = _match_entries(
        text, "transition_openers", patterns.get("transition_openers", []), output_category="banned_word"
    )
    if transition_hits:
        hits_by_category.setdefault("banned_word", []).extend(transition_hits)

    hedge_hits = _match_entries(
        text, "hedges", patterns.get("hedges", []), output_category="banned_word"
    )
    if hedge_hits:
        hits_by_category.setdefault("banned_word", []).extend(hedge_hits)

    clusters = _transition_clusters(text)
    if clusters:
        hits_by_category["transition_cluster"] = clusters

    stats = _sentence_stats(text)
    em_hits = _em_dash_hits(stats["em_dash_count"])
    if em_hits:
        hits_by_category["em_dash"] = em_hits

    all_hits = [hit for group in hits_by_category.values() for hit in group]
    auto_fixable = any(hit.get("auto_fixable") for hit in all_hits)
    needs_judgment = any(hit.get("needs_judgment") for hit in all_hits)

    return {
        "hits": hits_by_category,
        "auto_fixable": auto_fixable,
        "needs_judgment": needs_judgment,
        "stats": stats,
    }
