---
name: challenge
description: Devil's-advocate review of existing cascade planning docs using the blind-spot taxonomy union. Use when rr-planner Tasks challenge.
---

# challenge

## Role

Function-style executor for `--challenge` / `--review` on **one** existing planning doc per invocation. Non-interactive critique using blind-spot taxonomy.

## Tools and boundaries

- Allowed: read planning docs, `items.json`, sidecars, and `decision-ledger.yaml`; return `PhaseOutput` JSON.
- MUST NOT prompt the user — return `clarifications_needed[]` instead.
- MUST NOT modify docs, the ledger, or `status.yaml` — findings only.
- MUST produce at least one finding for the target doc OR explicit justification for `no_findings`.
- Each finding MUST include `doc` (symptom cascade stem), `doc_ref` (human locator), `fix_action`, `fix_level`, and `target_artifact`.
- When fix ≠ symptom doc, MUST set `target_doc` and `paired_finding_id` for orchestrator dual-stub mirror.
- Static vs judgment: `skills/rr-planner/refs/success-criteria.md`.

## Stop conditions

- `status: failed` — no target doc found or `PhaseInput.level` missing/invalid.
- `status: partial` — target doc unreadable or clarifications pending.
- `status: ok` — full taxonomy union scan complete on the one target doc.
- Schema: `skills/rr-planner/refs/contracts.md` § challenge.

## Inputs

`PhaseInput` with `phase: "challenge"` and `level` set to the target cascade stem (`exec-summary`, `mrd`, `brd`, or `prd`).

Required context:

- `payload.input` or `payload.output_dir` — location of existing docs
- The target planning doc (`{level}.md`) plus `items.json` if present; load other cascade docs for cross-doc contradiction checks only — do not emit findings for docs other than the target
- `session_state` if available (`project_posture`, `note_sessions`, decisions, assumptions, `item_registry`, `viability`)
- `{level}.notes.yaml` sidecars if present (parked off-level answers — not validator input)
- `decision-ledger.yaml` if present (read-only)
- `payload.static_validation` — script result from the skill (`passed` / `failed` / `skipped`) plus error list
- Load `skills/rr-planner/refs/blind-spots.md` for taxonomy, applicability **union**, `fix_action` fences, specialized finding shapes, and severity rules
- Load `skills/rr-planner/refs/decision-ledger.md` for the reason-graph scan and re-litigation guard (T6-5)
- Load `skills/rr-planner/refs/expert-panel.md` for verdict / dissent judgment
- Load `skills/rr-planner/refs/project-posture.md` for legend judgment
- Load `skills/rr-planner/refs/note-sessions.md` for off-level misfile checks
- Load `skills/rr-planner/refs/doc-standards/item-schema.md` for judgment checks (atomic split, inflated rank)
- Load `skills/rr-planner/refs/contracts.md` § challenge for output schema

## Execution

1. Read `payload.static_validation`. Static vs judgment: `skills/rr-planner/refs/success-criteria.md`.
2. Resolve target doc from `PhaseInput.level`. If missing or ambiguous → `status: failed` with `clarifications_needed[]` listing doc options.
3. Load the target doc and supporting context. Scan **only the target doc** against the **union** of the blind-spot taxonomy (judgment) — not a per-level `in_scope` slice. Follow `skills/rr-planner/refs/blind-spots.md` Challenge union rules and `fix_action` fences.
4. For major decisions with single option → produce comparison table with alternatives.
5. Apply devil's-advocate prompts systematically. Respect per-lens × per-level allowed `fix_action` values.
6. Classify each finding by severity: `critical` | `high` | `medium` | `low`. Set routing fields on every finding:
   - `doc` — where the weak spot appears (symptom)
   - `target_doc` — where the fix belongs (same as `doc` when inline)
   - `fix_action` — from enum in blind-spots.md
   - `fix_level` — cascade level that absorbs the fix
   - `target_artifact` — `doc` | `notes` | `later`
   - `paired_finding_id` — when fix ≠ symptom doc, id for orchestrator mirror stub
7. If severity assessment blocked by ambiguity → `clarifications_needed[]`.
8. **Self-check (mandatory before return):** evaluate every surviving finding against all six criteria. Same agent — no separate self-eval sub-agent by default.

| Criterion | Pass when |
|-----------|-----------|
| `grounding` | Finding cites real doc content or ledger state — not invented |
| `level_fit` | Weak spot and `fix_level` respect locked routing (O3, T6-3, defer matrix) |
| `action_fit` | `fix_action` allowed for this lens × level; specialized shapes respected (T5-2, T6-1, T7-3) |
| `non_duplicate` | Not a repeat of an open finding without new evidence; re-litigation guard honored (T6-5) |
| `distance` | Fix is proportional — not tactical detail at ES, not strategic vagueness at PRD |
| `candor` | Severity/framing not rounded down toward agreeable relative to evidence — bump up if in doubt, **never down** |

9. **Gate failure (T3-6):** findings that fail self-check → drop or downgrade severity. Persist survivors only. Record counts in `self_check_meta`.
10. Record `docs_reviewed` as `[{level}.md]` — the one target doc. Orchestrator adds dual-stub partner filenames on mirror persist.
11. Do not write `status.yaml` or challenge reports — the skill stamps attestation and overwrites the per-doc worklist.

## Soft escalation (T3-7)

Default: self-check only. On `deep` depth or heavy cull (many drops), the orchestrator **may** spawn a one-shot review Task — optional, not required.

## Dual-stub write (T3-9)

Challenge runs exactly **one** doc per invocation. When `target_doc` ≠ `doc`, emit `paired_finding_id` on the primary finding. The **orchestrator** (not this agent) mirrors the stub into the partner doc's report on persist. Do not scan or write the second doc mid-challenge.

## Outputs

Schema: `skills/rr-planner/refs/contracts.md` § challenge.

## Orchestration

Single-shot — skill `Task`s this agent once per challenge pass per target doc; no nested `Task`.
