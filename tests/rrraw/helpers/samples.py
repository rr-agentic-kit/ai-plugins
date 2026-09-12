"""Sample cascade docs and ledger blobs for rrraw tests."""

from __future__ import annotations

VALID_FILES: dict[str, str] = {
    "executive-summary.md": """\
# Exec summary

## ES-1: Competitive window
_parent_: — | _kind_: leaf | _spec_: ready

> Why now.

## ES-2: Regulatory ceiling
_parent_: — | _kind_: leaf | _spec_: ready | _tag_: regulatory

> Constraint.

## ES-3: Guest checkout
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
_parent_: PRD-1 | _kind_: leaf | _spec_: ready | _reach_: 40% of monthly active users | _impact_: 2 | _confidence_: medium | _effort_: 5

> As a guest, I can complete checkout without an account.
""",
}

VALID_YAML_FILES: dict[str, str] = {
    "executive-summary.yaml": """\
doc_type: executive-summary
title: Exec summary
items:
  ES-1:
    title: Competitive window
    Parent: —
    Kind: leaf
    Spec: ready
    body: |
      Why now.
  ES-2:
    title: Regulatory ceiling
    Parent: —
    Kind: leaf
    Spec: ready
    Tag: regulatory
    body: |
      Constraint.
  ES-3:
    title: Guest checkout
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
    Reach: 40% of monthly active users
    Impact: "2"
    Confidence: medium
    Effort: "5"
    body: |
      As a guest, I can complete checkout without an account.
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
    because: "Guest checkout is the functional deliverable the rest of the cascade stands on"
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
graveyard: {}
reserved_ids: {}
re_decision_queue: []
"""

RATIONALE_FILES: dict[str, str] = {
    "executive-summary.md": """\
# Exec summary

## ES-1: Competitive window
_parent_: — | _kind_: leaf | _spec_: ready | _rationale_: r-006

> Why now.

## ES-2: Regulatory ceiling
_parent_: — | _kind_: leaf | _spec_: ready | _tag_: regulatory | _rationale_: r-007

> Constraint.

## ES-3: Guest checkout
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
_parent_: PRD-1 | _kind_: leaf | _spec_: ready | _reach_: 40% of monthly active users | _impact_: 2 | _confidence_: medium | _effort_: 5 | _rationale_: r-004

> As a guest, I can complete checkout without an account.
""",
}

RATIONALE_YAML_FILES: dict[str, str] = {
    "executive-summary.yaml": """\
doc_type: executive-summary
title: Exec summary
items:
  ES-1:
    title: Competitive window
    Parent: —
    Kind: leaf
    Spec: ready
    Rationale: r-006
    body: |
      Why now.
  ES-2:
    title: Regulatory ceiling
    Parent: —
    Kind: leaf
    Spec: ready
    Tag: regulatory
    Rationale: r-007
    body: |
      Constraint.
  ES-3:
    title: Guest checkout
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
    Reach: 40% of monthly active users
    Impact: "2"
    Confidence: medium
    Effort: "5"
    Rationale: r-004
    body: |
      As a guest, I can complete checkout without an account.
""",
}

OLD_ES_FILES: dict[str, str] = {
    "executive-summary.md": """\
# Exec summary

## Vision

Guest checkout growth.

## Why now

Market window closing.

## ES-1: Competitive window
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must

> Incumbent launches in Q3.

## Success metrics

## ES-2: Self-serve conversion rate
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must

> 15% of visitors complete purchase without an account.

## ES-3: Multi-language support
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Should

> Product ships in English and Spanish at launch.

## Constraints

## ES-4: Regulatory ceiling
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Must

> Must comply with PCI scope limits.

## Non-goals

## ES-5: Enterprise SSO
_parent_: — | _kind_: leaf | _spec_: ready | _moscow_: Won't

> Out of scope for this initiative.
""",
}

OLD_PRD_FILES: dict[str, str] = {
    "mrd.md": """\
# MRD

## MRD-1: Account-free purchase
_parent_: ES-2 | _kind_: leaf | _spec_: ready | _kano_: basic
""",
    "brd.md": """\
# BRD

## BRD-1: Increase self-serve revenue
_parent_: MRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Must
""",
    "prd.md": """\
# PRD

## Product overview

Guest checkout for SMB buyers.

## Goals

## PRD-1: Grow self-serve revenue
_parent_: BRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Must

## User stories / outcomes

## PRD-2: Guest checkout
_parent_: PRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Must

> As a guest shopper, I can pay without creating an account.

## Features

## PRD-3: One-click reorder
_parent_: PRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Should

> Returning guests can reorder from email links.

## Release phasing

Unsigned legend: Must ships in MVP; Should in v1.1; Could later.

## Out of scope

## PRD-4: Native mobile apps
_parent_: PRD-1 | _kind_: leaf | _spec_: ready | _moscow_: Won't
""",
}

OLD_CHALLENGE_REPORT = """\
---
depth: deep
scanned_digest: sha256:deadbeef
---

# Challenge report

## bs-001 — prd (high)

- **doc:** prd
- **target_doc:** prd
- **severity:** high
- **category:** failure_modes
- **doc_ref:** prd.md § goals
- **finding:** No rollback strategy for failed migration
- **evidence:** PRD describes migration but no revert path
- **recommendation:** Add rollback acceptance criteria
- **fix_action:** flag_risk
- **fix_level:** prd
- **target_artifact:** doc

## bs-002 — executive-summary (medium)

- **doc:** executive-summary
- **target_doc:** executive-summary
- **severity:** medium
- **category:** scope_misfiling
- **doc_ref:** executive-summary.md § ES-3
- **finding:** Language support filed without metric teeth
- **evidence:** ES-3 is Should without a success metric anchor
- **recommendation:** Refile to functional deliverables or add metric
- **fix_action:** refile
- **fix_level:** executive-summary
- **target_artifact:** doc
"""

OLD_FRD_FILE = """\
# FRD

## FRD-1: Guest checkout API
_parent_: PRD-2 | _kind_: leaf | _spec_: ready | _build_: net-new | _class_: functional | _magnitude_: high

> The checkout service shall accept guest carts without account creation.

## FRD-2: Payment tokenization
_parent_: PRD-2 | _kind_: leaf | _spec_: draft | _build_: extend | _class_: integration | _magnitude_: medium

> Integrate with PCI-compliant token vault.
"""
