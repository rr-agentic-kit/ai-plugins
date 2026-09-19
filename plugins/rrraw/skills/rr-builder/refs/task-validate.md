# Task validate rubric

**Audience:** `rr-builder` orchestration after all task-steps for one task finish (post review / refactor stub). Assessment only — no application source edits.

## Inputs

| Input | Source |
|-------|--------|
| Task artifact | `docs/rr/tasks/{slice_id}/{NNNN}.md` |
| Goal / Obligations / Verify | Task body sections |
| Evidence | Diffs, test results, step notes from build/review |

## Rubric

| Check | PASS when | FAIL when |
|-------|-----------|-----------|
| **Goal** | Observable Goal outcome is met in the working tree / runnable verify | Goal unmet or only partially delivered without explicit Non-goals carve-out |
| **Verify / done** | Every Verify / done criterion is evidenced (command output, artifact, or cited proof) | Any Verify item missing, skipped, or contradicted |
| **Obligations** | Cited constitution / tech ADR / delta obligations still hold for changed surfaces | Obligation violated or silently ignored |
| **Non-goals** | Non-goals were not implemented as scope creep | Non-goal work shipped as if in-scope |
| **Open risks** | Residual risks either closed or explicitly carried with owner | Blocking `pending_tech` / open risk ignored as if done |

## Verdict

Emit one line: `task-validate: PASS | FAIL` plus ≤5 bullets of evidence (cite section + proof). On **FAIL**, leave `builder_stage: task_validate` and do not advance to next task or slice validate.

## Out of scope

- Slice-level AC / execute-slice outcome → [slice-validate.md](slice-validate.md)
- Re-running full rr-review (already done at review stage)
- Inventing new acceptance criteria not in the task file
