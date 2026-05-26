---
name: context-engineer-audit
description: Audit one agent context definition with static script plus severity rubric (report only).
---

# Audit

## Input contract

**REQUIRED:** plugin-relative path to the definition file.

## Execution

### Progress

Before any other step:

1. Execute **Action: audit** in skill **recipe-context-engineer** (follow skill **Run:** to load the internal procedure).
2. Call **TodoWrite** with `merge: false` and one todo per step (`audit-1-load` … `audit-5-report`).
3. Mark each todo `completed` before starting the next. Do not skip steps.

Diagnosis only—do not edit unless the user separately asks or runs fix/redesign.

## Output

- Verdict **PASS** only if all static and judgment checks pass; severity summary; static + judgment tables with evidence; narrative findings mapped to failure patterns.
- Any FAIL → recommend `/context-engineer-fix` for the same path (contract change → `/context-engineer-redesign`).
