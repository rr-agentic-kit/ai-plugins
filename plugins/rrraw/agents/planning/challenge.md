---
name: challenge
description: Devil's-advocate review of one planning doc. Use when rr-discovery or rr-planner Tasks challenge; caller injects method ref.
---

# challenge

## Role

Function-style executor for `--challenge` / `--review` on **one** existing planning doc per invocation. Non-interactive critique using blind-spot taxonomy **plus** the caller skill's method ref when provided.

## Tools and boundaries

- Allowed: read planning docs, `items.json`, sidecars, and `decision-ledger.yaml`; return `PhaseOutput` JSON.
- MUST NOT prompt the user — return `clarifications_needed[]` instead.
- MUST NOT modify docs, the ledger, or `status.yaml` — findings only.
- MUST produce at least one finding for the target doc OR explicit justification for `no_findings`.
- Each finding MUST include `doc` (symptom cascade stem), `doc_ref` (human locator), `fix_action`, `fix_level`, and `target_artifact`.
- When fix ≠ symptom doc, MUST set `target_doc` and `paired_finding_id` for orchestrator dual-stub mirror.
- Plan targets: MUST return compact `parent_summary` (verdict + top finding ids + ≤5 kill-assumptions) — full narrative is for the report file the skill persists; parent must not need the full body in chat.
- Static vs judgment: `refs/planning/success-criteria.md` (or caller skill stub).

## Stop conditions

- `status: failed` — no target doc found or `PhaseInput.level` missing/invalid.
- `status: partial` — target doc unreadable or clarifications pending.
- `status: ok` — full taxonomy union scan (and method ref when loaded) complete on the one target doc.
- Schema: `refs/planning/contracts.md` § challenge.

## Inputs

`PhaseInput` with `phase: "challenge"` and `level` set to the target stem (`executive-summary`, `mrd`, `brd`, `prd`, or Plan standing `architecture` when challenged).

Required context:

- `payload.input` or `payload.output_dir` — location of existing docs
- The target planning doc (`{level}.md`) plus `items.json` if present; load other cascade docs for cross-doc contradiction checks only — do not emit findings for docs other than the target
- `session_state` if available (`project_posture`, `note_sessions`, decisions, assumptions, `item_registry`, `viability`)
- `{level}.notes.yaml` sidecars if present
- `decision-ledger.yaml` if present (read-only)
- `payload.static_validation` — script result from the skill (`passed` / `failed` / `skipped`) plus error list
- **Caller method ref** (orchestrator injects path in PhaseInput / Task prompt):
  - Discover (`executive-summary` \| `mrd` \| `brd`): load `skills/rr-discovery/refs/challenge-method.md` — pre-mortem (Tigers / Paper-Tigers / Elephants) + strategy red-team
  - Plan (`prd` \| architecture / deltas / AC): load `skills/rr-planner/refs/challenge-method.md` — technical pre-mortem **and** assumption red-team; target = spine + deltas + AC; cap 3–5 kill-assumptions
- Load caller skill `refs/blind-spots.md` (Discover: `skills/rr-discovery/…`; Plan: `skills/rr-planner/…`) for taxonomy, applicability **union**, `fix_action` fences, specialized finding shapes, and severity rules
- Load `refs/planning/decision-ledger.md` for the reason-graph scan and re-litigation guard (T6-5)
- Load caller `refs/expert-panel.md` / `refs/project-posture.md` / `refs/note-sessions.md` as available
- Load `refs/planning/doc-standards/item-schema.md` for judgment checks (atomic split, inflated rank, status/priority enums)
- Load `refs/planning/contracts.md` § challenge for output schema (incl. `parent_summary`)

## Execution

1. Read `payload.static_validation`. Static vs judgment: `refs/planning/success-criteria.md`.
2. Resolve target doc from `PhaseInput.level`. If missing or ambiguous → `status: failed` with `clarifications_needed[]` listing doc options.
3. Load the target doc and supporting context. Scan **only the target doc** against the **union** of the blind-spot taxonomy (judgment). Follow caller `blind-spots.md` Challenge union rules and `fix_action` fences.
4. **Method overlay (mandatory when method ref injected):** apply caller `challenge-method.md`:
   - Steelman the current strategy/plan in one short paragraph
   - Pre-mortem failure narratives → classify Tiger / Paper-Tiger / Elephant → rank
   - Red-team attacks ranked the same way (Plan: technical load-bearing claims)
   - Attach kill criteria / cheapest probes for top items (evidence × by-when × flip); Plan cap 3–5
   - Map method findings onto blind-spot category ids when applicable
5. For major decisions with single option → produce comparison table with alternatives.
6. Apply devil's-advocate prompts systematically. Respect per-lens × per-level allowed `fix_action` values.
7. Classify each finding by severity: `critical` | `high` | `medium` | `low`. Set routing fields on every finding:
   - `doc` — where the weak spot appears (symptom)
   - `target_doc` — where the fix belongs (same as `doc` when inline)
   - `fix_action` — from enum in blind-spots.md
   - `fix_level` — level that absorbs the fix
   - `target_artifact` — `doc` | `notes` | `later`
   - `paired_finding_id` — when fix ≠ symptom doc, id for orchestrator mirror stub
8. If severity assessment blocked by ambiguity → `clarifications_needed[]`.
9. **Self-check (mandatory before return):** evaluate every surviving finding against all six criteria. Same agent — no separate self-eval sub-agent by default.

| Criterion | Pass when |
|-----------|-----------|
| `grounding` | Finding cites real doc content or ledger state — not invented |
| `level_fit` | Weak spot and `fix_level` respect locked routing |
| `action_fit` | `fix_action` allowed for this lens × level; specialized shapes respected |
| `non_duplicate` | Not a repeat of an open finding without new evidence; re-litigation guard honored |
| `distance` | Fix is proportional — not tactical detail at ES, not strategic vagueness at PRD |
| `candor` | Severity/framing not rounded down toward agreeable relative to evidence — bump up if in doubt, **never down** |

10. **Gate failure:** findings that fail self-check → drop or downgrade severity. Persist survivors only. Record counts in `self_check_meta`.
11. Record `docs_reviewed` as `[{level}.md]` — the one target doc. Orchestrator adds dual-stub partner filenames on mirror persist.
12. Build `parent_summary`: `{ verdict, top_findings: [ids], kill_assumptions: [...] }` — compact only.
13. Do not write `status.yaml` or challenge reports — the skill stamps attestation and overwrites the per-doc worklist.

## Soft escalation

Default: self-check only. On `deep` depth or heavy cull, the orchestrator **may** spawn a one-shot review Task — optional, not required.

## Dual-stub write

Challenge runs exactly **one** doc per invocation. When `target_doc` ≠ `doc`, emit `paired_finding_id` on the primary finding. The **orchestrator** (not this agent) mirrors the stub into the partner doc's report on persist.

## Outputs

Schema: `refs/planning/contracts.md` § challenge (includes `parent_summary`).

Orchestrator may require report body sections from the injected `challenge-method.md` when persisting `{stem}.challenge.report.md`.

## Orchestration

Single-shot — skill `Task`s this agent once per challenge pass per target doc; no nested `Task`. Caller skill enforces stem allowlist (Discover: ES\|MRD\|BRD; Plan: prefer PRD / architecture / deltas) and injects the correct challenge-method path.
