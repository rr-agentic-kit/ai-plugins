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

## ES-1: Guest checkout growth
- **Parent:** —
- **Kind:** leaf
- **Spec:** ready
- **MoSCoW:** —

Vision.

## ES-2: Account wall drop-off
- **Parent:** —
- **Kind:** leaf
- **Spec:** ready
- **MoSCoW:** —

Problem.

## ES-3: Self-serve conversion
- **Parent:** —
- **Kind:** leaf
- **Spec:** ready
- **MoSCoW:** Must
""",
    "mrd.md": """\
# MRD

## MRD-1: SMB buyers
- **Parent:** ES-2
- **Kind:** leaf
- **Spec:** ready
- **Kano:** —

Primary segment.

## MRD-2: Account-free purchase
- **Parent:** ES-2
- **Kind:** leaf
- **Spec:** ready
- **Kano:** basic
""",
    "brd.md": """\
# BRD

## BRD-1: Increase self-serve revenue
- **Parent:** MRD-2
- **Kind:** leaf
- **Spec:** ready
- **MoSCoW:** Must
""",
    "prd.md": """\
# PRD

## PRD-1: Checkout
- **Parent:** BRD-1
- **Kind:** container
- **Spec:** draft

### PRD-1.1: Guest checkout
- **Parent:** PRD-1
- **Kind:** leaf
- **Spec:** ready
- **MoSCoW:** Must

As a guest, I can complete checkout without an account.
""",
    "frd.md": """\
# FRD

## FRD-1: Checkout
- **Parent:** PRD-1.1
- **Kind:** container
- **Spec:** draft

### FRD-1.1: Guest checkout without account
- **Parent:** FRD-1
- **Kind:** leaf
- **Spec:** ready
- **Build:** in_progress
- **If present:** high — Unlocks self-serve conversion without an account
- **If absent:** high — PLG blocked
- **If wrong:** critical — Bad tax/entitlements
- **Class:** must-correct

The system shall allow checkout without an account.
""",
}

VALID_YAML_FILES: dict[str, str] = {
    "exec-summary.yaml": """\
doc_type: exec-summary
title: Exec summary
items:
  ES-1:
    title: Guest checkout growth
    Parent: —
    Kind: leaf
    Spec: ready
    MoSCoW: —
    body: |
      Vision.
  ES-2:
    title: Account wall drop-off
    Parent: —
    Kind: leaf
    Spec: ready
    MoSCoW: —
    body: |
      Problem.
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
    title: SMB buyers
    Parent: ES-2
    Kind: leaf
    Spec: ready
    Kano: —
    body: |
      Primary segment.
  MRD-2:
    title: Account-free purchase
    Parent: ES-2
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
    Parent: MRD-2
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


def write_planning(
    root: Path,
    files: dict[str, str] | None = None,
    *,
    items: list[dict[str, Any]] | None = None,
    session: dict[str, Any] | None = None,
    write_json: bool = True,
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    payload = files if files is not None else VALID_FILES
    for name, content in payload.items():
        (root / name).write_text(content, encoding="utf-8")
    if write_json:
        if items is None:
            md_items, _ = vp.parse_planning_dir(root)
            items = [item.to_record() for item in md_items]
        (root / "items.json").write_text(
            json.dumps({"items": items}, indent=2) + "\n", encoding="utf-8"
        )
    if session is not None:
        (root / "session-state.json").write_text(
            json.dumps(session, indent=2) + "\n", encoding="utf-8"
        )
    return root


def codes(issues: list[vp.Issue]) -> set[str]:
    return {issue.code for issue in issues}


def error_codes(issues: list[vp.Issue]) -> set[str]:
    return {issue.code for issue in issues if issue.severity == "error"}
