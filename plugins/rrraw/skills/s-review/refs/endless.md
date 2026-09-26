# Endless review: exit conditions

**Audience:** **s-review** when `endless: true` — always when `outcome: fix` (orchestrate review **and** handoff `--fix`; `--endless` alone still requires / forces fix). Shape mirrors s-test-endless exit caps without coverage heuristics.

**Default `--max-epochs`:** **5**.

## Loop shape

Each **epoch** `n` (1-based):

1. Assess all selected lanes (epoch-stamped stems — [artifacts.md](artifacts.md)).
2. Challenge (consumers use **keep** only).
3. Fix per [fix-routing.md](fix-routing.md) (`outcome: fix` required).
4. Re-assess / evaluate exit rules below.
5. Overwrite `REVIEW_DIR/report.md` each epoch.

Re-enter fix routing after a non-clear epoch when `n < max_epochs` — see [fix-routing.md](fix-routing.md).

## Residual probe (before treating zero-keep as clear)

When Challenge yields **zero `keep`** in code+test (candidate clear or warnings-security-only), run this **residual probe** before exit success. Do **not** invent findings outside these checks; if a check fails, emit new `keep` row(s) and continue the epoch loop (do not exit `pass`/`warnings` yet).

| Trigger in current MR / allowlist | Probe |
|-----------------------------------|-------|
| New or changed **auth / hooks / guard / session** production paths | Matching **test** pairing present (unit and/or e2e covering the new guard); missing → `keep` under **test** (or **code** if production gap) |
| **≥3** near-duplicate modules / helpers for the same concern (e.g. repeated scope guards, copy-pasted nav builders) | DRY scan — consolidate or justify; unjustified duplication → `keep` under **code** |

Skip a row only when the trigger is absent from scope. Probe is mandatory on every candidate-clear epoch — including epoch 1.

## Clear report (success)

After Challenge **and** residual probe on the latest assess:

| Decision | Condition |
|----------|-----------|
| **`pass`** | Zero `keep` rows in **all** lanes (code, test, security) **and** residual probe clean |
| **`warnings`** | Zero `keep` in **code** and **test**; residual probe clean; one or more security-only `keep`s remain (unfixable) |

Either outcome is **endless exit success**. Orchestrate may set `step_review_done: true` **only if** `docs/rr/tasks/{slice_id}/{NNNN}-{step}.review.md` also exists (parent `refs/slice-pipeline.md` review done-when / sidecar hard-stop).

Security-only `keep`s are **not** fixable under `--fix`; do not burn epochs trying to clear them.

## Exit rules (after each Challenge / re-assess)

Evaluate **OR**:

1. **Clear / pass** — zero `keep` all lanes **and** residual probe clean → exit success, decision `pass`.
2. **Warnings-security-only** — code+test clear; residual probe clean; security keeps remain → exit success, decision `warnings`.
3. **Epoch cap** — current epoch equals `--max-epochs` (default 5) and neither (1) nor (2) → stop; do **not** set `step_review_done`; orchestrate hard-stops the chain.

## Hard stop (non-success)

| Trigger | Effect |
|---------|--------|
| Incompatible flags / empty allowlist / policy abort | Stop before or during loop; no success exit |
| Assess failed for a lane needed by `--fix` | Skip that lane’s fix; note in report; continue epoch evaluation |
| Unchallenged challengeable rows | **Stopped:** `unchallenged report` |
| Epoch cap without clear/warnings | Leave report with remaining keeps; chat notes max-epochs; orchestrate leaves `step_review_done` unset |

## Chat / report

- Success (orchestrate with task/step cursor): announce `docs/rr/tasks/{slice_id}/{NNNN}-{step}.review.md` with decision `pass` or `warnings` (scratch still under `.ai/review/<runId>/`).
- Success (handoff without cursor): announce `Report written: .ai/review/<runId>/report.md` with decision `pass` or `warnings`.
- Cap: announce the same terminal path used for the run; decision not pass/warnings-success; note epochs exhausted; orchestrate leaves `step_review_done` unset.
