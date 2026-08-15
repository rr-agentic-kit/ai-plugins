# compose

Function-style executor for rendering one planning doc from accumulated facts. Parameterized by `doc_type`. Non-interactive — returns `clarifications_needed[]` on gaps.

## Input

`PhaseInput` with `phase: "compose"`.

Required context:

- `payload.output_dir`, `payload.format`, `payload.depth`
- `level` / `doc_type`: one of `exec-summary`, `mrd`, `brd`, `prd`, `frd`
- `session_state.level_facts` for current and parent levels
- `session_state.decisions`, `session_state.assumptions`
- `session_state.item_registry`, `session_state.frozen_levels`
- Load matching `doc-standards/<doc_type>.md` for structure and done-when
- Load [item-schema.md](../../skills/rr-planner/refs/doc-standards/item-schema.md) for IDs, split, parent, spec/build, templates
- Load [contracts.md](../../skills/rr-planner/refs/contracts.md) § compose for output schema

## Execution

1. Read doc-standard + item-schema — required sections, which are items vs prose, this level’s `priority_method`.
2. Gather facts from `session_state.level_facts[doc_type]` and inherited parent facts.
3. **Split compounds** before minting: one leaf = one testable statement. Multiple shalls/actors/outcomes → container + `n.1…n.k` leaves. Containers have no shall.
4. **Mint IDs** `{DOC}-{n}` / `{DOC}-{n.m}`:
   - Level not in `frozen_levels`: dense among siblings (`1, 2, 3`).
   - Frozen: append next integer; do not reuse or pack gaps.
   - Re-compose of a frozen level: emit a remap of old id → new id; skill rewrites child-doc `parent:` via `item_registry`.
5. Set `parent:` to the immediate parent only (same-doc container or previous-level item). ES roots: `—`. Do not print the full chain.
6. Fill the **level’s** priority method on leaves (MoSCoW / Kano / triad). Unranked leaves: native key `—`. Containers: unmarked.
7. **FRD:** inherit `if_absent` magnitude from parent PRD MoSCoW (Must → high, Should → moderate, Could → low). Do not compose children of Won’t. Fill `if_wrong`; set `Class` from the item-schema partition. Do not copy MoSCoW onto FRD.
8. **Status:** default new items `spec: idea`. Set `draft` when this compose is specifying them. Never auto-promote to `ready` (user/gate). Never set `build` except FRD leaves (`none` until `spec: ready`). Replacement: new id `draft`/`idea` + `supersedes`; old id `deprecated` + `superseded_by` immediately.
9. Render markdown with closed heading + metadata vocabulary (item-schema templates). Body after the blank line is free markdown. End the file with the item index table.
10. Emit `items[]` records matching contracts (same data as markdown headers). Skill writes `items.json` and merges `item_registry`.
11. For each required section with insufficient facts: do not invent; add `ClarificationItem` (`severity: blocking` or `high`).
12. Set `sections_completed` and `sections_incomplete` explicitly.

Static ref/status checks are **not** this agent’s job — skill runs `validate_planning.py`. Compose still must emit parseable headers so the script can pass.

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
- Do not write files — return `doc_content` + `items[]`; skill writes to `--output-dir`.
- One doc per invocation; skill calls once per cascade level.
- Do not promote `spec` to `ready` just because fields are filled.
