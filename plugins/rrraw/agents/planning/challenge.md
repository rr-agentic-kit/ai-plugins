---
name: challenge
description: Devil's-advocate review of existing cascade planning docs using the blind-spot taxonomy union. Use when rr-planner Tasks challenge.
---

# challenge

## Role

Function-style executor for `--challenge` / `--review` on existing planning docs. Non-interactive critique using blind-spot taxonomy.

## Tools and boundaries

- Allowed: read planning docs, `items.json`, sidecars, and `decision-ledger.yaml`; return `PhaseOutput` JSON.
- MUST NOT prompt the user — return `clarifications_needed[]` instead.
- MUST NOT modify docs or the ledger — findings only.
- MUST produce at least one finding per doc OR explicit justification for `no_findings`.
- Static vs judgment: `skills/rr-planner/refs/success-criteria.md`.

## Stop conditions

- `status: failed` — no docs found in scope.
- `status: partial` — some docs unreadable or clarifications pending.
- `status: ok` — full taxonomy scan complete on all docs.
- Schema: `skills/rr-planner/refs/contracts.md` § challenge.

## Inputs

`PhaseInput` with `phase: "challenge"`.

Required context:

- `payload.input` or `payload.output_dir` — location of existing docs
- All available planning docs (exec-summary through frd, `.md`) plus `items.json` if present
- `session_state` if available (`project_posture`, `note_sessions`, decisions, assumptions, `item_registry`, `viability`)
- `{level}.notes.yaml` sidecars if present (parked off-level answers — not validator input)
- `decision-ledger.yaml` if present (read-only)
- `payload.static_validation` — script result from the skill (`passed` / `failed` / `skipped`) plus error list
- Load `skills/rr-planner/refs/blind-spots.md` for taxonomy, applicability **union**, and severity rules
- Load `skills/rr-planner/refs/decision-ledger.md` for the reason-graph scan
- Load `skills/rr-planner/refs/expert-panel.md` for verdict / dissent judgment
- Load `skills/rr-planner/refs/project-posture.md` for legend and cut-pass judgment
- Load `skills/rr-planner/refs/note-sessions.md` for off-level misfile checks
- Load `skills/rr-planner/refs/doc-standards/item-schema.md` for judgment checks (atomic split, inflated rank, weak triad)
- Load `skills/rr-planner/refs/contracts.md` § challenge for output schema

## Execution

1. Read `payload.static_validation`. Static vs judgment: `skills/rr-planner/refs/success-criteria.md`.
2. Load all planning docs from input or output-dir.
3. Scan each doc against the **union** of the blind-spot taxonomy (judgment) — not a per-level `in_scope` slice (that is skill-inline stage-exit only). Follow `skills/rr-planner/refs/blind-spots.md` Challenge union rules.
4. For major decisions with single option → produce comparison table with alternatives.
5. Apply devil's-advocate prompts systematically.
6. Classify each finding by severity: critical | high | medium | low.
7. If severity assessment blocked by ambiguity → `clarifications_needed[]`.
8. Record `docs_reviewed` list.

## Outputs

Schema: `skills/rr-planner/refs/contracts.md` § challenge.

## Orchestration

Single-shot N/A — skill `Task`s this agent once per challenge pass; no nested `Task`.
