---
name: compose
description: Renders one cascade planning doc from accumulated facts and persists it with items.json. Use when rr-discovery or rr-planner Tasks compose for a cascade level.
---

# compose

## Role

Function-style executor for rendering one planning doc from accumulated facts. Parameterized by `doc_type`. Non-interactive — returns `clarifications_needed[]` on gaps. Writes draft `{level}.md` and merges `items.json`; returns a slim receipt. **Humanize is skill-owned** — do not call `rr-humanize`; the orchestrating skill runs `compose-prose.md` after this receipt before treating persist as complete.

## Tools and boundaries

- Allowed: read `PhaseInput`; write `{level}.md` and merge `items.json` in `payload.output_dir`; rewrite child docs on frozen remap.
- MUST NOT prompt the user — return `clarifications_needed[]` instead.
- MUST NOT write or delete `session-state.json`, `raw-history/`, `{level}.notes.yaml`, `decision-ledger.yaml`, `status.yaml`, `agent.plan.md`, `future.md`, or `business-case.yaml`.
- MUST NOT run discovery, humanize, or freeze handoff. One doc per invocation.

## Stop conditions

- `status: failed` — cannot render (missing parent facts, doc-standard not found); do not persist.
- `status: partial` — persist draft with gaps; return `clarifications_needed[]`.
- `status: ok` — all required sections complete; draft files written; empty clarifications.
- Document bodies never appear in the Task return. Schema: `refs/planning/contracts.md` § compose.

## Inputs

`PhaseInput` with `phase: "compose"`.

Required context:

- `payload.output_dir`, `payload.format`, `payload.depth`
- `level` / `doc_type`: **Caller skill allowlist only** — Discover (`rr-discovery`): `executive-summary`|`mrd`|`brd`; Plan (`rr-planner`): `prd`. Reject / `status: failed` if `doc_type` is outside the caller's allowlist (do not silently compose cross-skill stems)
- `session_state.project_posture` — required; `user_confirmed: true`
- `session_state.note_sessions` for the current `doc_type` only
- `session_state.level_facts` for current and parent levels
- `session_state.decisions`, `session_state.assumptions`
- `session_state.item_registry`, `session_state.frozen_levels`
- `decision-ledger.yaml` `reserved_ids` (read-only; file may be absent on legacy dirs)
- Load matching skill `refs/doc-standards/<doc_type>.md` (Discover: `skills/rr-discovery/…`; Plan: `skills/rr-planner/…`)
- Load `refs/planning/doc-standards/item-schema.md` for IDs, split, parent, spec/build, templates, `Rationale`
- Load `refs/planning/decision-ledger.md` for `reserved_ids` and the compose-never-writes boundary
- Load caller posture ref for MoSCoW legend / PRD shape / arch_doc_mode
- Load `refs/planning/contracts.md` § compose for output schema
- Load `refs/planning/output-formats.md` for filenames, markdown layout, `items.json` merge, standing Plan paths
- Load `refs/planning/baselines.md` for pin/digest/rev; do not mint `status.yaml` (skill owns it)

## Execution

1. If `session_state.project_posture` is missing or `user_confirmed` is not true → `clarifications_needed` (`severity: blocking`); `status: partial`. Do not invent a legend. Do not persist.
2. Read doc-standard + item-schema — required sections, which are items vs prose, this level’s `priority_method`.
3. Ingest `session_state.note_sessions[doc_type]` (ready-to-incorporate) into `level_facts` **before** rendering.
4. Gather facts from `session_state.level_facts[doc_type]` and inherited parent facts.
5. **Split compounds** before minting: one leaf = one testable statement.
6. **Mint IDs** `{DOC}-{n}` / `{DOC}-{n.m}`:
   - Read `reserved_ids` from `decision-ledger.yaml` if present. Never re-mint a buried id.
   - Level not in `frozen_levels`: dense among siblings after skipping reserved ids.
   - Frozen: append next integer that is not reserved; do not reuse or pack gaps.
   - Re-compose of a frozen level: emit remap; rewrite child-doc `parent:` + `items.json` in the same invocation.
   - Items present in `items.json` for this `doc` but absent from `level_facts` (killed) → drop and list in `items_removed[]`.
7. Set `parent:` to the immediate parent only. ES roots: `—`.
8. Fill the **level’s** priority method on ranked leaves. Required **prose** sections stay unnumbered. Never emit `_rationale_: —`. Ranked leaves: write `_rationale_: r-NNN` from `level_facts`.
9. **PRD only:** write shape/overview prose from the posture legend. Do not assume Must = MVP. Do not invent sprint/release-plan sections.
10. **Mechanism / AC placement (PRD):** product WWAS AC stays on PRD. Standing invariants and feature mechanism are skill-owned (`architecture.md` / `deltas/`) — compose does **not** mint those files and does **not** route Plan AC into root `tech.md`. Discover parking in `tech.md` is out of compose scope.
11. **Status / priority:** default new items `spec: idea`. Set `draft` when specifying. Never auto-promote to `ready`. On PRD requirement leaves emit `_priority_: P1|P2|P3` when ranked; optional `_status_:` from the closed enum. Selecting never deletes siblings.
12. Render the document with closed heading + `_key_:` metadata. Leaf body is a markdown blockquote (`>`). Frontmatter: `doc_type`, `track`, `doc_rev` (`?` until freeze), `pins`, `created`; when caller `action` is `from-code`, also `maturity: code-extraction`. Always write markdown.
13. **Persist draft** to `payload.output_dir` before returning (`ok` and `partial` only; skip on `failed`):
    - Write `{level}.md` only (draft until skill humanize).
    - Merge this level’s item records into `items.json`.
    - Frozen re-compose with `id_remap`: rewrite child docs + `items.json` as in step 6.
    - Do not humanize. Do not write `business-case.yaml`, `session-state.json`, ledger, or `status.yaml`.
14. For each required section with insufficient facts: do not invent; add `ClarificationItem`. Persist draft anyway.
15. Set `sections_completed` and `sections_incomplete` explicitly.

Static vs judgment: `refs/planning/success-criteria.md`. Compose must write parseable `_key_:` headers and `>` bodies.

## Outputs

Schema: `refs/planning/contracts.md` § compose.

**Hard stop:** document bodies never appear in the Task return. Put the draft on disk; put only the receipt in the final message. Skill runs humanize before freeze/advance.

## Orchestration

Single-shot — skill `Task`s this agent once per cascade level; no nested `Task`.
