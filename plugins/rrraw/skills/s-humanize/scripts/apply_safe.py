from __future__ import annotations

import re
from typing import Any

from scan import _SENTENCE_SPLIT, load_patterns, scan_text

_CHATBOT_DROP = re.compile(
    r"(?im)^\s*(?:"
    r"I hope this helps[.!]?\s*|"
    r"Great question[!]?\s*|"
    r"(?:As of my (?:last )?knowledge cutoff|My training data)[^.!?]*[.!?]\s*|"
    r"Let me know if (?:you(?:'d| would) like|there's anything)[^.!?]*[.!?]\s*"
    r")$"
)


def _apply_replacements(text: str, entries: list[dict[str, Any]]) -> tuple[str, list[dict[str, str]]]:
    changes: list[dict[str, str]] = []
    updated = text
    for entry in entries:
        if not entry.get("auto_fixable"):
            continue
        if entry.get("action") == "drop_sentence":
            continue
        replacement = entry.get("replacement")
        if replacement is None:
            continue
        flags = re.IGNORECASE if "i" in entry.get("flags", "") else 0
        pattern = re.compile(entry["pattern"], flags)
        new_text, count = pattern.subn(replacement, updated)
        if count:
            changes.append(
                {
                    "id": entry["id"],
                    "count": str(count),
                    "replacement": replacement,
                }
            )
            updated = new_text
    return updated, changes


def _drop_chatbot_sentences(text: str) -> tuple[str, list[dict[str, str]]]:
    changes: list[dict[str, str]] = []
    sentences = _SENTENCE_SPLIT.split(text)
    kept: list[str] = []
    for sentence in sentences:
        if _CHATBOT_DROP.match(sentence.strip()):
            changes.append({"id": "chatbot_sentence", "match": sentence.strip()})
        else:
            kept.append(sentence)
    if not kept:
        return text, changes
    return " ".join(kept), changes


def apply_safe_text(text: str, *, dry_run: bool = False) -> dict[str, Any]:
    patterns = load_patterns()
    before_scan = scan_text(text)
    if not before_scan["auto_fixable"]:
        return {
            "dry_run": dry_run,
            "changed": False,
            "text": text,
            "changes": [],
            "before_hits": before_scan["hits"],
        }

    updated = text
    all_changes: list[dict[str, str]] = []

    for category in ("filler", "copula_avoidance", "quote_normalization"):
        updated, changes = _apply_replacements(updated, patterns.get(category, []))
        all_changes.extend(changes)

    updated, chat_changes = _drop_chatbot_sentences(updated)
    all_changes.extend(chat_changes)

    # Normalize whitespace after drops
    updated = re.sub(r"  +", " ", updated)
    updated = re.sub(r"\n{3,}", "\n\n", updated).strip()

    changed = updated != text
    result: dict[str, Any] = {
        "dry_run": dry_run,
        "changed": changed,
        "changes": all_changes,
        "before_hits": before_scan["hits"],
    }
    if dry_run:
        result["preview"] = updated
    else:
        result["text"] = updated
    return result
