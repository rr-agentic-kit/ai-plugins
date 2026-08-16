# compose

Function-style executor for rendering one planning doc from accumulated facts. Parameterized by `doc_type`. Non-interactive — returns `clarifications_needed[]` on gaps. **Persists** the doc and `items.json`; returns a slim receipt.

## Input

`PhaseInput` with `phase: "compose"`.

Required context:

- `payload.output_dir`, `payload.format`, `payload.depth`
- `level` / `doc_type`: one of `exec-summary`, `mrd`, `brd`, `prd`, `frd`
- `session_state.project_posture` — required; `user_confirmed: true`
- `session_state.note_sessions` for the current `doc_type` only (skill may also pass sidecar contents)
- `session_state.level_facts` for current and parent levels
- `session_state.decisions`, `session_state.assumptions`
- `session_state.item_registry`, `session_state.frozen_levels`
- Load matching `doc-standards/<doc_type>.md` for structure and done-when
- Load [item-schema.md](../../skills/rr-planner/refs/doc-standards/item-schema.md) for IDs, split, parent, spec/build, templates
- Load [project-posture.md](../../skills/rr-planner/refs/project-posture.md) for MoSCoW legend and PRD release-phasing
- Load [contracts.md](../../skills/rr-planner/refs/contracts.md) § compose for output schema
- Load [output-formats.md](../../skills/rr-planner/refs/output-formats.md) for filenames, md/yaml layout, and `items.json` merge

## Execution

1. If `session_state.project_posture` is missing or `user_confirmed` is not true → `clarifications_needed` (`severity: blocking`); `status: partial`. Do not invent a legend. Do not persist.
2. Read doc-standard + item-schema — required sections, which are items vs prose, this level’s `priority_method`.
3. Ingest `session_state.note_sessions[doc_type]` (ready-to-incorporate) into `level_facts` **before** rendering. Ignore notes whose `doc_type` is not the current level. Do not mint items from another level's sidecar.
4. Gather facts from `session_state.level_facts[doc_type]` and inherited parent facts.
5. **Split compounds** before minting: one leaf = one testable statement. Multiple shalls/actors/outcomes → container + `n.1…n.k` leaves. Containers have no shall.
6. **Mint IDs** `{DOC}-{n}` / `{DOC}-{n.m}`:
   - Level not in `frozen_levels`: dense among siblings (`1, 2, 3`).
   - Frozen: append next integer; do not reuse or pack gaps.
   - Re-compose of a frozen level: emit a remap of old id → new id. In the **same invocation**, rewrite child-doc `parent:` fields and matching `items.json` records so children do not point at vanished ids. Skill does not rewrite child docs.
7. Set `parent:` to the immediate parent only (same-doc container or previous-level item). ES roots: `—`. Do not print the full chain.
8. Fill the **level’s** priority method on leaves (MoSCoW / Kano / triad) using the posture legend for PRD/ES MoSCoW. Unranked leaves: native key `—`. Containers: unmarked. Exec-summary must include the unranked Posture leaf.
9. **PRD:** write release-phasing prose from the posture legend; state which 2×2 cell was used. Do not assume Must = MVP. Do not emit a `horizon:` field.
10. **FRD:** inherit `if_absent` magnitude from parent PRD MoSCoW (Must → high, Should → moderate, Could → low). Do not compose children of Won’t. Fill `if_wrong`; set `Class` from the item-schema partition. Do not copy MoSCoW onto FRD.
11. **Status:** default new items `spec: idea`. Set `draft` when this compose is specifying them. Never auto-promote to `ready` (user/gate). Never set `build` except FRD leaves (`none` until `spec: ready`). Replacement: new id `draft`/`idea` + `supersedes`; old id `deprecated` + `superseded_by` immediately.
12. Render the document with closed heading + metadata vocabulary (item-schema templates). Body after the blank line is free markdown. End markdown files with the item index table. When `payload.format` is `yaml`, serialize closed-key YAML yourself — parent does not serialize.
13. **Persist** to `payload.output_dir` before returning (`ok` and `partial` only; skip on `failed`):
    - Write `{level}.md` or `{level}.yaml` per `payload.format`.
    - Merge this level’s item records into `items.json` (read-modify-write: replace only this `doc`’s records; do not clobber other levels). Create the file if missing.
    - Frozen re-compose with `id_remap`: rewrite child docs + `items.json` as in step 6.
    - Files on disk are drafts until the skill adds this level to `frozen_levels`. Intra-session re-compose overwrites without asking.
    - Do not write `session-state.json`, `raw-history/`, or `{level}.notes.yaml`.
14. For each required section with insufficient facts: do not invent; add `ClarificationItem` (`severity: blocking` or `high`). Persist anyway — drafts may have gaps.
15. Set `sections_completed` and `sections_incomplete` explicitly.

Static ref/status checks are **not** this agent’s job — skill reads `items.json` and runs `validate_planning.py`. Compose still must write parseable headers so the script can pass. Sidecars are not validator input and are not items.

## Output

`PhaseOutput` with slim `data` per [contracts.md](../../skills/rr-planner/refs/contracts.md) § compose.

**Hard stop:** document bodies never appear in the Task return — not in `data`, not in `summary`, not as a preamble. Put the doc on disk; put only the receipt in the final message.

| Field | In `data` |
|-------|-----------|
| `doc_type` | Current level |
| `doc_path` | Path of the file just written (`{level}.md` or `{level}.yaml`) |
| `sections_completed` | Required sections with content |
| `sections_incomplete` | Required sections with gaps |
| `clarifications_needed` | `ClarificationItem[]` — non-empty blocks `status: ok` |
| `id_remap` | Old id → new id when re-composing a frozen level; `{}` otherwise |
| `assumptions_used` | Assumption ids referenced in doc |

No `doc_content`. No `items[]`. `artifacts[]` = paths **this agent wrote** this invocation (`doc_path`, `items.json`, rewritten child docs if any).

| `status` | When |
|----------|------|
| `ok` | All required sections complete; `clarifications_needed` empty; files persisted |
| `partial` | Doc persisted but gaps remain (`sections_incomplete` non-empty or clarifications present) |
| `failed` | Cannot render (missing parent level facts, doc-standard not found) — do not persist |

## Constraints

- **Non-interactive** — never prompt user; return `clarifications_needed[]` instead.
- Do not run discovery — consume facts provided in `session_state`.
- Require confirmed `project_posture`; do not invent a MoSCoW legend.
- Consume notes for the current `doc_type` only; do not mint items from another level's sidecar.
- Persist `{level}.md|yaml` and merge `items.json` before returning. Document bodies never appear in the Task return.
- One doc per invocation; skill calls once per cascade level.
- Do not promote `spec` to `ready` just because fields are filled.
- Do not write `session-state.json`, `raw-history/`, or `{level}.notes.yaml`.
