"""Factories for planning trees, items, and issue helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import validate_planning_script as vp

from .samples import VALID_FILES


def write_planning(
    root: Path,
    files: dict[str, str] | None = None,
    *,
    items: list[dict[str, Any]] | None = None,
    session: dict[str, Any] | None = None,
    ledger: str | None = None,
    write_json: bool = True,
    status: dict[str, Any] | None = None,
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    payload = files if files is not None else VALID_FILES
    for name, content in payload.items():
        (root / name).write_text(content, encoding="utf-8")
    if write_json:
        if items is None:
            collected: list[vp.Item] = []
            for name in payload:
                stem = name.rsplit(".", 1)[0]
                if stem not in vp.DOC_STEMS:
                    continue
                text = (root / name).read_text(encoding="utf-8")
                if name.endswith(".yaml"):
                    parsed, _ = vp.parse_yaml_doc(text, name)
                else:
                    parsed, _ = vp.parse_markdown(text, name, migrate=True)
                collected.extend(parsed)
            items = [item.to_record() for item in collected]
        (root / "items.json").write_text(
            json.dumps({"items": items}, indent=2) + "\n", encoding="utf-8"
        )
    if session is not None:
        (root / "session-state.json").write_text(
            json.dumps(session, indent=2) + "\n", encoding="utf-8"
        )
    if ledger is not None:
        (root / "decision-ledger.yaml").write_text(ledger, encoding="utf-8")
    if status is not None:
        payload_status = dict(status)
        if "mint_hash" not in payload_status:
            payload_status["mint_hash"] = vp.compute_mint_hash(payload_status)
        vp.write_status_yaml(root / "status.yaml", payload_status)
    return root


def planning_items(root: Path) -> list[vp.Item]:
    items, _ = vp.parse_planning_dir(root)
    return items


def frozen_status(
    items: list[vp.Item],
    *,
    track: str = "0.1",
    product: str = "0.1.3",
    docs: str = "0.1.7",
    next_track: str | None = None,
    frozen: list[str] | None = None,
    docs_shipped: bool = True,
    claude_config_version: int = 1,
) -> dict[str, Any]:
    frozen_set = set(frozen if frozen is not None else list(vp.DOC_STEMS))
    levels: dict[str, Any] = {}
    for doc in vp.DOC_STEMS:
        parent = vp.PARENT_DOC.get(doc)
        if doc in frozen_set:
            rev: int | str = 1
            digest: str | None = vp.compute_doc_digest(items, doc)
        else:
            rev = "?"
            digest = None
        pins: dict[str, Any] = {}
        if parent and doc in frozen_set and parent in frozen_set:
            pins[parent] = {
                "rev": 1,
                "digest": vp.compute_doc_digest(items, parent),
            }
        levels[doc] = {"rev": rev, "digest": digest, "pins": pins}
    data: dict[str, Any] = {
        "claude_config_version": claude_config_version,
        "track": track,
        "product": product,
        "docs": docs,
        "next": next_track,
        "docs_shipped": docs_shipped,
        "product_status": "shipped" if docs_shipped else "?",
        "levels": levels,
        "next_levels": {},
        "challenge": {},
        "next_challenge": {},
    }
    data["mint_hash"] = vp.compute_mint_hash(data)
    return data


def codes(issues: list[vp.Issue]) -> set[str]:
    return {issue.code for issue in issues}


def error_codes(issues: list[vp.Issue]) -> set[str]:
    return {issue.code for issue in issues if issue.severity == "error"}


_UNSET = object()

PRD_RICE_DEFAULTS = {
    "reach": "40% of monthly active users",
    "impact": "2",
    "confidence": "medium",
    "effort": "5",
}


def prd_rice(
    item_id: str,
    *,
    parent: str | object | None = _UNSET,
    spec: str = "ready",
    **kwargs: Any,
) -> vp.Item:
    rice = {**PRD_RICE_DEFAULTS, **kwargs}
    return item(item_id, parent=parent, spec=spec, **rice)


def item(
    item_id: str,
    *,
    title: str = "x",
    parent: str | object | None = _UNSET,
    kind: str = "leaf",
    spec: str = "ready",
    status: str | None = None,
    tag: str | None = None,
    goal_type: str | None = None,
    reach: str | None = None,
    impact: str | None = None,
    confidence: str | None = None,
    effort: str | None = None,
    moscow: str | None = None,
    kano: str | None = None,
    supersedes: str | None = None,
    superseded_by: str | None = None,
    rationale: str | None = None,
    source_file: str = "",
    raw_keys: set[str] | None = None,
    raw_meta: dict[str, str] | None = None,
) -> vp.Item:
    prefix = item_id.split("-", 1)[0]
    doc = vp.PREFIX_TO_DOC[prefix]
    resolved_parent = None if parent is _UNSET else parent
    keys = set(raw_keys) if raw_keys is not None else {"parent", "kind", "spec"}
    if raw_keys is None:
        if status is not None:
            keys.add("status")
        if tag is not None:
            keys.add("tag")
        if goal_type is not None:
            keys.add("goal-type")
        if reach is not None:
            keys.add("reach")
        if impact is not None:
            keys.add("impact")
        if confidence is not None:
            keys.add("confidence")
        if effort is not None:
            keys.add("effort")
        if moscow is not None:
            keys.add("moscow")
        if kano is not None:
            keys.add("kano")
        if rationale is not None:
            keys.add("rationale")
        if supersedes is not None:
            keys.add("supersedes")
        if superseded_by is not None:
            keys.add("superseded-by")
    meta = dict(raw_meta) if raw_meta is not None else {}
    return vp.Item(
        id=item_id,
        title=title,
        prefix=prefix,
        doc=doc,
        parent=resolved_parent,  # type: ignore[arg-type]
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
        raw_keys=keys,
        raw_meta=meta,
    )
