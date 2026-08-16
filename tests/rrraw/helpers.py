"""Helpers for rrraw validate_planning tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "plugins" / "rrraw" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import validate_planning as vp  # noqa: E402

VALID_FILES: dict[str, str] = {
    "exec-summary.md": """\
# Exec summary

## ES-1: Competitive window
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must

> Why now.

## ES-2: Regulatory ceiling
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must

> Constraint.

## ES-3: Self-serve conversion
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must
""",
    "mrd.md": """\
# MRD

## MRD-1: Account-free purchase
_parent_: ES-3 | _kind_: leaf | _spec_: ready | _kano_: basic
""",
    "brd.md": """\
# BRD

## BRD-1: Increase self-serve revenue
_parent_: MRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Must
""",
    "prd.md": """\
# PRD

## PRD-1: Checkout
_parent_: BRD-1 | _kind_: container | _spec_: draft

### PRD-1.1: Guest checkout
_parent_: PRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Must

> As a guest, I can complete checkout without an account.
""",
    "frd.md": """\
# FRD

## FRD-1: Checkout
_parent_: PRD-1.1 | _kind_: container | _spec_: draft

### FRD-1.1: Guest checkout without account
_parent_: FRD-1 | _kind_: leaf | _spec_: ready | _build_: in_progress | _if-present_: high — Unlocks self-serve conversion without an account | _if-absent_: high — PLG blocked | _if-wrong_: critical — Bad tax/entitlements | _class_: must-correct

> The system shall allow checkout without an account.
""",
}

VALID_YAML_FILES: dict[str, str] = {
    "exec-summary.yaml": """\
doc_type: exec-summary
title: Exec summary
items:
  ES-1:
    title: Competitive window
    Parent: —
    Kind: leaf
    Spec: ready
    MoSCoW: Must
    body: |
      Why now.
  ES-2:
    title: Regulatory ceiling
    Parent: —
    Kind: leaf
    Spec: ready
    MoSCoW: Must
    body: |
      Constraint.
  ES-3:
    title: Self-serve conversion
    Parent: —
    Kind: leaf
    Spec: ready
    MoSCoW: Must
""",
    "mrd.yaml": """\
doc_type: mrd
title: MRD
items:
  MRD-1:
    title: Account-free purchase
    Parent: ES-3
    Kind: leaf
    Spec: ready
    Kano: basic
""",
    "brd.yaml": """\
doc_type: brd
title: BRD
items:
  BRD-1:
    title: Increase self-serve revenue
    Parent: MRD-1
    Kind: leaf
    Spec: ready
    MoSCoW: Must
""",
    "prd.yaml": """\
doc_type: prd
title: PRD
items:
  PRD-1:
    title: Checkout
    Parent: BRD-1
    Kind: container
    Spec: draft
  PRD-1.1:
    title: Guest checkout
    Parent: PRD-1
    Kind: leaf
    Spec: ready
    MoSCoW: Must
    body: |
      As a guest, I can complete checkout without an account.
""",
    "frd.yaml": """\
doc_type: frd
title: FRD
items:
  FRD-1:
    title: Checkout
    Parent: PRD-1.1
    Kind: container
    Spec: draft
  FRD-1.1:
    title: Guest checkout without account
    Parent: FRD-1
    Kind: leaf
    Spec: ready
    Build: in_progress
    "If present": high — Unlocks self-serve conversion without an account
    "If absent": high — PLG blocked
    "If wrong": critical — Bad tax/entitlements
    Class: must-correct
    body: |
      The system shall allow checkout without an account.
""",
}


VALID_LEDGER = """\
version: 1
evidence:
  e-001:
    claim: "Obtainable share reaches 10% by year 3"
    status: supported
    confidence: high
    sources:
      - { title: "Internal analog", url: "https://example.invalid/analog", accessed: 2026-08-16 }
rationales:
  r-001:
    decision: accept
    subject: ES-3
    seat: seed-investor
    because: "Self-serve conversion is the ES metric the rest of the cascade stands on"
    depends_on: [e-001]
    flips_when:
      - { kind: fact, evidence: e-001, becomes: refuted }
    condition_strength: observable
    status: live
  r-006:
    decision: accept
    subject: ES-1
    seat: seed-investor
    because: "The competitive window is the why-now that justifies this session"
    depends_on: [e-001]
    flips_when:
      - { kind: event, text: "Incumbent ships guest checkout natively" }
    condition_strength: observable
    status: live
  r-007:
    decision: accept
    subject: ES-2
    seat: domain-practitioner
    because: "Regulatory ceiling is a hard constraint on the metric"
    depends_on: [e-001]
    flips_when:
      - { kind: event, text: "The named regime no longer applies" }
    condition_strength: observable
    status: live
  r-002:
    decision: accept
    subject: MRD-1
    seat: growth-investor
    because: "Account-free purchase is a basic need for the SMB segment"
    depends_on: [e-001]
    flips_when:
      - { kind: event, text: "Primary segment shifts to enterprise procurement" }
    condition_strength: observable
    status: live
  r-003:
    decision: accept
    subject: BRD-1
    seat: cfo
    because: "Self-serve revenue is the business outcome of the ES metric"
    depends_on: [e-001]
    flips_when:
      - { kind: metric, metric: self_serve_revenue_share, op: "<", value: 0.05 }
    condition_strength: measurable
    status: live
  r-004:
    decision: accept
    subject: PRD-1.1
    seat: head-of-product
    because: "Guest checkout is the product capability that moves ES-3"
    depends_on: [e-001]
    flips_when:
      - { kind: fact, evidence: e-001, becomes: refuted }
    condition_strength: observable
    status: live
  r-005:
    decision: accept
    subject: FRD-1.1
    seat: staff-engineer
    because: "Shall is the implementable form of PRD-1.1"
    depends_on: [e-001]
    flips_when:
      - { kind: event, text: "Tax/entitlement engine cannot run without an account" }
    condition_strength: observable
    status: live
graveyard: {}
reserved_ids: {}
re_decision_queue: []
"""

RATIONALE_FILES: dict[str, str] = {
    "exec-summary.md": """\
# Exec summary

## ES-1: Competitive window
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must | _rationale_: r-006

> Why now.

## ES-2: Regulatory ceiling
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must | _rationale_: r-007

> Constraint.

## ES-3: Self-serve conversion
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must | _rationale_: r-001
""",
    "mrd.md": """\
# MRD

## MRD-1: Account-free purchase
_parent_: ES-3 | _kind_: leaf | _spec_: ready | _kano_: basic | _rationale_: r-002
""",
    "brd.md": """\
# BRD

## BRD-1: Increase self-serve revenue
_parent_: MRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Must | _rationale_: r-003
""",
    "prd.md": """\
# PRD

## PRD-1: Checkout
_parent_: BRD-1 | _kind_: container | _spec_: draft

### PRD-1.1: Guest checkout
_parent_: PRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Must | _rationale_: r-004

> As a guest, I can complete checkout without an account.
""",
    "frd.md": """\
# FRD

## FRD-1: Checkout
_parent_: PRD-1.1 | _kind_: container | _spec_: draft

### FRD-1.1: Guest checkout without account
_parent_: FRD-1 | _kind_: leaf | _spec_: ready | _build_: in_progress | _if-present_: high — Unlocks self-serve conversion without an account | _if-absent_: high — PLG blocked | _if-wrong_: critical — Bad tax/entitlements | _class_: must-correct | _rationale_: r-005

> The system shall allow checkout without an account.
""",
}

RATIONALE_YAML_FILES: dict[str, str] = {
    "exec-summary.yaml": """\
doc_type: exec-summary
title: Exec summary
items:
  ES-1:
    title: Competitive window
    Parent: —
    Kind: leaf
    Spec: ready
    MoSCoW: Must
    Rationale: r-006
    body: |
      Why now.
  ES-2:
    title: Regulatory ceiling
    Parent: —
    Kind: leaf
    Spec: ready
    MoSCoW: Must
    Rationale: r-007
    body: |
      Constraint.
  ES-3:
    title: Self-serve conversion
    Parent: —
    Kind: leaf
    Spec: ready
    MoSCoW: Must
    Rationale: r-001
""",
    "mrd.yaml": """\
doc_type: mrd
title: MRD
items:
  MRD-1:
    title: Account-free purchase
    Parent: ES-3
    Kind: leaf
    Spec: ready
    Kano: basic
    Rationale: r-002
""",
    "brd.yaml": """\
doc_type: brd
title: BRD
items:
  BRD-1:
    title: Increase self-serve revenue
    Parent: MRD-1
    Kind: leaf
    Spec: ready
    MoSCoW: Must
    Rationale: r-003
""",
    "prd.yaml": """\
doc_type: prd
title: PRD
items:
  PRD-1:
    title: Checkout
    Parent: BRD-1
    Kind: container
    Spec: draft
  PRD-1.1:
    title: Guest checkout
    Parent: PRD-1
    Kind: leaf
    Spec: ready
    MoSCoW: Must
    Rationale: r-004
    body: |
      As a guest, I can complete checkout without an account.
""",
    "frd.yaml": """\
doc_type: frd
title: FRD
items:
  FRD-1:
    title: Checkout
    Parent: PRD-1.1
    Kind: container
    Spec: draft
  FRD-1.1:
    title: Guest checkout without account
    Parent: FRD-1
    Kind: leaf
    Spec: ready
    Build: in_progress
    "If present": high — Unlocks self-serve conversion without an account
    "If absent": high — PLG blocked
    "If wrong": critical — Bad tax/entitlements
    Class: must-correct
    Rationale: r-005
    body: |
      The system shall allow checkout without an account.
""",
}


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
    }
    data["mint_hash"] = vp.compute_mint_hash(data)
    return data


def codes(issues: list[vp.Issue]) -> set[str]:
    return {issue.code for issue in issues}


def error_codes(issues: list[vp.Issue]) -> set[str]:
    return {issue.code for issue in issues if issue.severity == "error"}
