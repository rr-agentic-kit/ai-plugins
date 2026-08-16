---
name: compose
description: Renders one cascade planning doc from accumulated facts and persists it with items.json. Use when rr-planner Tasks compose for a cascade level.
---

# compose

## Role

Function-style executor for rendering one planning doc from accumulated facts. Parameterized by `doc_type`. Non-interactive — returns `clarifications_needed[]` on gaps. Persists the doc and `items.json`; returns a slim receipt.

## Tools and boundaries

- Allowed: read `PhaseInput`; write `{level}.md` and merge `items.json` in `payload.output_dir`; rewrite child docs on frozen remap.
- MUST NOT prompt the user — return `clarifications_needed[]` instead.
- MUST NOT write or delete `session-state.json`, `raw-history/`, `{level}.notes.yaml`, or `decision-ledger.yaml`.
- MUST NOT run discovery. One doc per invocation.

## Stop conditions

- `status: failed` — cannot render (missing parent facts, doc-standard not found); do not persist.
- `status: partial` — persist with gaps; return `clarifications_needed[]`.
- `status: ok` — all required sections complete; files persisted; empty clarifications.
- Document bodies never appear in the Task return. Schema: `skills/rr-planner/refs/contracts.md` § compose.

## Inputs

`PhaseInput` with `phase: "compose"`.

Required context:

- `payload.output_dir`, `payload.format`, `payload.depth`
- `level` / `doc_type`: one of `exec-summary`, `mrd`, `brd`, `prd`, `frd`
- `session_state.project_posture` — required; `user_confirmed: true`
- `session_state.note_sessions` for the current `doc_type` only (skill may also pass sidecar contents)
- `session_state.level_facts` for current and parent levels
- `session_state.decisions`, `session_state.assumptions`
- `session_state.item_registry`, `session_state.frozen_levels`
- `decision-ledger.yaml` `reserved_ids` (read-only; file may be absent on legacy dirs)
- Load matching `skills/rr-planner/refs/doc-standards/<doc_type>.md` for structure and done-when
- Load `skills/rr-planner/refs/doc-standards/item-schema.md` for IDs, split, parent, spec/build, templates, `Rationale`
- Load `skills/rr-planner/refs/decision-ledger.md` for `reserved_ids` and the compose-never-writes boundary
- Load `skills/rr-planner/refs/project-posture.md` for MoSCoW legend and PRD release-phasing
- Load `skills/rr-planner/refs/contracts.md` § compose for output schema
- Load `skills/rr-planner/refs/output-formats.md` for filenames, markdown layout, and `items.json` merge

## Execution

1. If `session_state.project_posture` is missing or `user_confirmed` is not true → `clarifications_needed` (`severity: blocking`); `status: partial`. Do not invent a legend. Do not persist.
2. Read doc-standard + item-schema — required sections, which are items vs prose, this level’s `priority_method`.
3. Ingest `session_state.note_sessions[doc_type]` (ready-to-incorporate) into `level_facts` **before** rendering — backstop only; the skill already loaded the sidecar on level entry. Ignore notes whose `doc_type` is not the current level. Do not mint items from another level's sidecar.
4. Gather facts from `session_state.level_facts[doc_type]` and inherited parent facts.
5. **Split compounds** before minting: one leaf = one testable statement. Multiple shalls/actors/outcomes → container + `n.1…n.k` leaves. Containers have no shall.
6. **Mint IDs** `{DOC}-{n}` / `{DOC}-{n.m}`:
   - Read `reserved_ids` from `decision-ledger.yaml` if present. Never re-mint a buried id (skip those integers / `n.m` pairs).
   - Level not in `frozen_levels`: dense among siblings (`1, 2, 3`) after skipping reserved ids.
   - Frozen: append next integer that is not reserved; do not reuse or pack gaps.
   - Re-compose of a frozen level: emit a remap of old id → new id. In the **same invocation**, rewrite child-doc `parent:` fields and matching `items.json` records so children do not point at vanished ids. Skill does not rewrite child docs.
   - Items present in `items.json` for this `doc` but absent from `level_facts` (killed) → drop from `items.json` and list in `items_removed[]`.
7. Set `parent:` to the immediate parent only (same-doc container or previous-level item). ES roots: `—`. Do not print the full chain.
8. Fill the **level’s** priority method on ranked leaves (MoSCoW / Kano / triad) using the posture legend for PRD/ES MoSCoW. Do not mint unranked leaves. Required **prose** sections stay unnumbered: ES Posture, Vision, Problem, What-must-be-true, Viability; MRD overview / sizing / segments / competitors / trends / risks; BRD Stakeholders, Business risks; PRD overview, User personas, release phasing. Containers: unmarked (no method key). Ranked `idea`/`draft` without a cut may emit `_moscow_: —` / `_kano_: —`; `ready` must have a real value. Never emit `_rationale_: —`. Ranked leaves: write `_rationale_: r-NNN` from `level_facts`. If a ranked leaf has no rationale id → `clarifications_needed` (`severity: blocking`); do not invent an `r-*`.
9. **PRD:** write release-phasing prose from the posture legend; state which 2×2 cell was used. Do not assume Must = MVP. Do not emit a `horizon:` field.
10. **FRD:** inherit `if_absent` magnitude from parent PRD MoSCoW (Must → high, Should → moderate, Could → low). Do not compose children of Won’t. Fill `if_wrong`; set `Class` from the item-schema partition. Do not copy MoSCoW onto FRD.
11. **Status:** default new items `spec: idea`. Set `draft` when this compose is specifying them. Never auto-promote to `ready` (user/gate). Never set `build` except FRD leaves (`none` until `spec: ready`). Replacement: new id `draft`/`idea` + `supersedes`; old id `deprecated` + `superseded_by` immediately.
12. Render the document with closed heading + `_key_:` metadata (item-schema templates). Leaf body is a markdown blockquote (`>`). End with the item index table. Always write markdown — `payload.format` is `md`; do not serialize YAML cascade docs.
13. **Persist** to `payload.output_dir` before returning (`ok` and `partial` only; skip on `failed`):
    - Write `{level}.md` only.
    - Merge this level’s item records into `items.json` (read-modify-write: replace only this `doc`’s records; do not clobber other levels). Create the file if missing.
    - Frozen re-compose with `id_remap`: rewrite child docs + `items.json` as in step 6.
    - Files on disk are drafts until the skill adds this level to `frozen_levels`. Intra-session re-compose overwrites without asking.
    - Do not write or delete `session-state.json`, `raw-history/`, `{level}.notes.yaml`, or `decision-ledger.yaml`. Skill prunes this level's sidecar after persist (`skills/rr-planner/refs/note-sessions.md`).
14. For each required section with insufficient facts: do not invent; add `ClarificationItem` (`severity: blocking` or `high`). Persist anyway — drafts may have gaps.
15. Set `sections_completed` and `sections_incomplete` explicitly.

Static vs judgment: `skills/rr-planner/refs/success-criteria.md`. Compose still must write parseable `_key_:` headers and `>` bodies so the script can pass. Sidecars are not validator input and are not items.

## Outputs

Schema: `skills/rr-planner/refs/contracts.md` § compose.

**Hard stop:** document bodies never appear in the Task return — not in `data`, not in `summary`, not as a preamble. Put the doc on disk; put only the receipt in the final message.

## Orchestration

Single-shot N/A — skill `Task`s this agent once per cascade level; no nested `Task`.
