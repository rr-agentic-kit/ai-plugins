# compose

Function-style executor for rendering one planning doc from accumulated facts. Parameterized by `doc_type`. Non-interactive — returns `clarifications_needed[]` on gaps.

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

## Execution

1. If `session_state.project_posture` is missing or `user_confirmed` is not true → `clarifications_needed` (`severity: blocking`); `status: partial`. Do not invent a legend.
2. Read doc-standard + item-schema — required sections, which are items vs prose, this level’s `priority_method`.
3. Ingest `session_state.note_sessions[doc_type]` (ready-to-incorporate) into `level_facts` **before** rendering. Ignore notes whose `doc_type` is not the current level. Do not mint items from another level's sidecar.
4. Gather facts from `session_state.level_facts[doc_type]` and inherited parent facts.
5. **Split compounds** before minting: one leaf = one testable statement. Multiple shalls/actors/outcomes → container + `n.1…n.k` leaves. Containers have no shall.
6. **Mint IDs** `{DOC}-{n}` / `{DOC}-{n.m}`:
   - Level not in `frozen_levels`: dense among siblings (`1, 2, 3`).
   - Frozen: append next integer; do not reuse or pack gaps.
   - Re-compose of a frozen level: emit a remap of old id → new id; skill rewrites child-doc `parent:` via `item_registry`.
7. Set `parent:` to the immediate parent only (same-doc container or previous-level item). ES roots: `—`. Do not print the full chain.
8. Fill the **level’s** priority method on leaves (MoSCoW / Kano / triad) using the posture legend for PRD/ES MoSCoW. Unranked leaves: native key `—`. Containers: unmarked. Exec-summary must include the unranked Posture leaf.
9. **PRD:** write release-phasing prose from the posture legend; state which 2×2 cell was used. Do not assume Must = MVP. Do not emit a `horizon:` field.
10. **FRD:** inherit `if_absent` magnitude from parent PRD MoSCoW (Must → high, Should → moderate, Could → low). Do not compose children of Won’t. Fill `if_wrong`; set `Class` from the item-schema partition. Do not copy MoSCoW onto FRD.
11. **Status:** default new items `spec: idea`. Set `draft` when this compose is specifying them. Never auto-promote to `ready` (user/gate). Never set `build` except FRD leaves (`none` until `spec: ready`). Replacement: new id `draft`/`idea` + `supersedes`; old id `deprecated` + `superseded_by` immediately.
12. Render the document with closed heading + metadata vocabulary (item-schema templates). Body after the blank line is free markdown. End markdown files with the item index table. When `payload.format` is `yaml`, still emit parseable `items[]`; the skill serializes closed-key YAML.
13. Emit `items[]` records matching contracts (same data as markdown headers). Skill writes `items.json` and merges `item_registry`.
14. For each required section with insufficient facts: do not invent; add `ClarificationItem` (`severity: blocking` or `high`).
15. Set `sections_completed` and `sections_incomplete` explicitly.

Static ref/status checks are **not** this agent’s job — skill runs `validate_planning.py`. Compose still must emit parseable headers so the script can pass. Sidecars are not validator input and are not items.

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-planner/refs/contracts.md) § compose.

| `status` | When |
|----------|------|
| `ok` | All required sections complete; `clarifications_needed` empty |
| `partial` | Doc rendered but gaps remain (`sections_incomplete` non-empty or clarifications present) |
| `failed` | Cannot render (missing parent level facts, doc-standard not found) |

## Constraints

- **Non-interactive** — never prompt user; return `clarifications_needed[]` instead.
- Do not run discovery — consume facts provided in `session_state`.
- Require confirmed `project_posture`; do not invent a MoSCoW legend.
- Consume notes for the current `doc_type` only; do not mint items from another level's sidecar.
- Do not write files — return `doc_content` + `items[]`; skill writes to `--output-dir`.
- One doc per invocation; skill calls once per cascade level.
- Do not promote `spec` to `ready` just because fields are filled.
