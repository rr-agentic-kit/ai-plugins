"""Decision ledger load and rationale pointers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .constants import (
    CONDITION_STRENGTHS,
    DOC_METHOD,
    EVIDENCE_ID_RE,
    EVIDENCE_STATUSES,
    FLIP_KINDS,
    METRIC_OPS,
    QUEUE_STATUSES,
    RATIONALE_DECISIONS,
    RATIONALE_RE,
    RATIONALE_STATUSES,
)
from .models import Issue, Item


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
            Issue.warn(
                "LEDGER_MISSING",
                f"missing {path.name}; rationale checks skipped",
            )
        ]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return None, [Issue.error("LEDGER_MALFORMED", f"{path.name}: {exc}")]
    if not isinstance(data, dict):
        return None, [Issue.error("LEDGER_MALFORMED", f"{path.name} must be a mapping")]
    issues = check_ledger_shape(data)
    if any(issue.severity == "error" for issue in issues):
        return data, issues
    return data, issues


def _check_evidence_record(eid: str, record: object) -> list[Issue]:
    if not isinstance(record, dict):
        return [
            Issue.error(
                "LEDGER_MALFORMED",
                f"{eid} must be a mapping",
                eid,
            )
        ]
    status = record.get("status")
    if status is not None and status not in EVIDENCE_STATUSES:
        return [
            Issue.error(
                "LEDGER_MALFORMED",
                f"evidence status {status!r} is not "
                "supported|refuted|unknown|superseded",
                eid,
            )
        ]
    return []


def _check_evidence_section(data: dict[str, Any]) -> tuple[set[str], list[Issue]]:
    issues: list[Issue] = []
    evidence = data.get("evidence", {})
    if "evidence" in data and not isinstance(evidence, dict):
        issues.append(Issue.error("LEDGER_MALFORMED", "evidence must be a mapping"))
        evidence = {}
    evidence_ids = {
        key for key in evidence if isinstance(key, str) and EVIDENCE_ID_RE.match(key)
    }
    for raw_id, record in evidence.items():
        eid = str(raw_id)
        if not EVIDENCE_ID_RE.match(eid):
            issues.append(
                Issue.error(
                    "LEDGER_MALFORMED",
                    f"malformed evidence id {eid!r}",
                    eid,
                )
            )
        issues.extend(_check_evidence_record(eid, record))
    return evidence_ids, issues


def _check_queue_section(
    data: dict[str, Any], rationales: dict[str, Any]
) -> list[Issue]:
    issues: list[Issue] = []
    queue = data.get("re_decision_queue", [])
    if "re_decision_queue" in data and not isinstance(queue, list):
        return [
            Issue.error(
                "LEDGER_MALFORMED",
                "re_decision_queue must be a list",
            )
        ]
    for index, entry in enumerate(queue):
        if not isinstance(entry, dict):
            issues.append(
                Issue.error(
                    "LEDGER_MALFORMED",
                    f"re_decision_queue[{index}] must be a mapping",
                )
            )
            continue
        status = entry.get("status")
        if status is not None and status not in QUEUE_STATUSES:
            issues.append(
                Issue.error(
                    "LEDGER_MALFORMED",
                    f"re_decision_queue[{index}] status {status!r}",
                )
            )
        pointer = entry.get("rationale")
        if pointer and pointer not in rationales:
            issues.append(
                Issue.error(
                    "BROKEN_RATIONALE",
                    f"queue points at unknown rationale {pointer}",
                )
            )
    return issues


def check_ledger_shape(data: dict[str, Any]) -> list[Issue]:
    evidence_ids, issues = _check_evidence_section(data)
    rationales = data.get("rationales", {})
    if not isinstance(rationales, dict):
        issues.append(Issue.error("LEDGER_MALFORMED", "rationales must be a mapping"))
        return issues
    for raw_id, record in rationales.items():
        rid = str(raw_id)
        if not RATIONALE_RE.match(rid):
            issues.append(
                Issue.error(
                    "LEDGER_MALFORMED",
                    f"malformed rationale id {rid!r}",
                    rid,
                )
            )
        if not isinstance(record, dict):
            issues.append(
                Issue.error(
                    "LEDGER_MALFORMED",
                    f"{rid} must be a mapping",
                    rid,
                )
            )
            continue
        issues.extend(_check_rationale_record(rid, record, evidence_ids))
    graveyard = data.get("graveyard", {})
    if "graveyard" in data and not isinstance(graveyard, dict):
        issues.append(Issue.error("LEDGER_MALFORMED", "graveyard must be a mapping"))
    reserved = data.get("reserved_ids", {})
    if "reserved_ids" in data and not isinstance(reserved, dict):
        issues.append(Issue.error("LEDGER_MALFORMED", "reserved_ids must be a mapping"))
    issues.extend(_check_queue_section(data, rationales))
    return issues


def _check_metric_flip(rid: str, index: int, entry: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    if not entry.get("metric") or entry.get("op") not in METRIC_OPS:
        issues.append(
            Issue.error(
                "LEDGER_MALFORMED",
                f"flips_when[{index}] metric requires metric and op "
                f"in {sorted(METRIC_OPS)}",
                rid,
            )
        )
    if "value" not in entry:
        issues.append(
            Issue.error(
                "LEDGER_MALFORMED",
                f"flips_when[{index}] metric requires value",
                rid,
            )
        )
    return issues


def _check_fact_flip(
    rid: str, index: int, entry: dict[str, Any], evidence_ids: set[str]
) -> list[Issue]:
    pointer = entry.get("evidence")
    if not isinstance(pointer, str) or not EVIDENCE_ID_RE.match(pointer):
        return [
            Issue.error(
                "LEDGER_MALFORMED",
                f"flips_when[{index}] fact requires evidence e-NNN",
                rid,
            )
        ]
    if pointer in evidence_ids:
        return []
    return [
        Issue.error(
            "BROKEN_RATIONALE",
            f"flips_when[{index}] evidence {pointer} does not exist",
            rid,
        )
    ]


def _check_flip_entry(
    rid: str, index: int, entry: object, evidence_ids: set[str]
) -> list[Issue]:
    if not isinstance(entry, dict):
        return [
            Issue.error(
                "LEDGER_MALFORMED",
                f"flips_when[{index}] must be a mapping",
                rid,
            )
        ]
    kind = entry.get("kind")
    if kind not in FLIP_KINDS:
        return [
            Issue.error(
                "LEDGER_MALFORMED",
                f"flips_when[{index}] kind must be metric|fact|event, got {kind!r}",
                rid,
            )
        ]
    if kind == "metric":
        return _check_metric_flip(rid, index, entry)
    if kind == "fact":
        return _check_fact_flip(rid, index, entry, evidence_ids)
    if str(entry.get("text") or "").strip():
        return []
    return [
        Issue.error(
            "LEDGER_MALFORMED",
            f"flips_when[{index}] event requires text",
            rid,
        )
    ]


def _check_rationale_record(
    rid: str, record: dict[str, Any], evidence_ids: set[str]
) -> list[Issue]:
    issues: list[Issue] = []
    decision = record.get("decision")
    if decision not in RATIONALE_DECISIONS:
        issues.append(
            Issue.error(
                "LEDGER_MALFORMED",
                f"decision must be accept|reject|postpone|pivot, got {decision!r}",
                rid,
            )
        )
    status = record.get("status")
    if status is not None and status not in RATIONALE_STATUSES:
        issues.append(
            Issue.error(
                "LEDGER_MALFORMED",
                f"status must be live|invalidated|superseded, got {status!r}",
                rid,
            )
        )
    strength = record.get("condition_strength")
    if strength is not None and strength not in CONDITION_STRENGTHS:
        issues.append(
            Issue.error(
                "LEDGER_MALFORMED",
                f"condition_strength must be measurable|observable|vague, "
                f"got {strength!r}",
                rid,
            )
        )
    flips = record.get("flips_when")
    if not isinstance(flips, list) or not flips:
        issues.append(
            Issue.error(
                "LEDGER_MALFORMED",
                "flips_when must be a non-empty list",
                rid,
            )
        )
        return issues
    for index, entry in enumerate(flips):
        issues.extend(_check_flip_entry(rid, index, entry, evidence_ids))
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
                Issue.error(
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
                Issue.error(
                    "BROKEN_RATIONALE",
                    f"rationale {rid} does not exist",
                    item.id,
                )
            )
    return issues
