# Plan-stage output schema

**Audience:** `rr-builder` orchestrate **plan** stage. Persist the plan under the active task’s **Steps** entry for `step_index` (or an adjacent `### Plan` block keyed to that step). **No** application source edits.

## Required sections

| Section | Content |
|---------|---------|
| **Goal of step** | One observable outcome for this step only |
| **Approach** | Mechanism-bearing plan (files/symbols/seams); cite allowlist refs used |
| **Risks** | Residual risks / unknowns that could block build |
| **Verify hooks** | How build will prove the step (commands, assertions, AC ids) |
| **Non-goals** | Explicit exclusions for this step |

## Done-when

All five sections present and non-empty; assessment is enough for **build** to start without inventing scope; **no** application source edits this stage. Then set `step_plan_done: true` on `{NNNN}.md` (see [slice-pipeline.md](slice-pipeline.md) cursor persistence).

## Anti-patterns

- Pasting full language matrices or implement Procedures into the plan body
- Editing application source “to explore”
- Omitting **Verify hooks** (pushes invent into build)
