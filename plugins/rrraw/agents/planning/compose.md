# compose

Function-style executor for rendering one planning doc from accumulated facts. Parameterized by `doc_type`. Non-interactive — returns `clarifications_needed[]` on gaps.

## Input

`PhaseInput` with `phase: "compose"`.

Required context:

- `payload.output_dir`, `payload.format`
- `level` / `doc_type`: one of `exec-summary`, `mrd`, `brd`, `prd`, `frd`
- `session_state.level_facts` for current and parent levels
- `session_state.decisions`, `session_state.assumptions`
- Load matching `doc-standards/<doc_type>.md` for structure and done-when
- Load [contracts.md](../../skills/rr-planner/refs/contracts.md) § compose for output schema

## Execution

1. Read doc-standard for `doc_type` — extract required sections and traceability rules.
2. Gather facts from `session_state.level_facts[doc_type]` and inherited parent facts.
3. Render full markdown document:
   - All required sections populated from facts.
   - Assign traceability ids per doc-standard.
   - Link child items to parent ids (`traces_to`, `goal_ref`).
   - Mark assumptions used with assumption ids.
4. For each required section with insufficient facts:
   - Do not invent content.
   - Add `ClarificationItem` to `clarifications_needed[]` with `severity: blocking` or `high`.
5. Validate internal consistency — no contradictions with parent level facts.
6. Set `sections_completed` and `sections_incomplete` explicitly.

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
- Do not write files — return `doc_content`; skill writes to `--output-dir`.
- One doc per invocation; skill calls once per cascade level.
