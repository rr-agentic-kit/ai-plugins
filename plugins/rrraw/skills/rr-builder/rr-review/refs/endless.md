# Endless review: exit conditions

**Audience:** **rr-review** when `endless: true` (orchestrate review always; handoff when `--endless`). Shape mirrors rr-test-endless exit caps without coverage heuristics.

**Default `--max-epochs`:** **5**.

## Loop shape

Each **epoch** `n` (1-based):

1. Assess all selected lanes (epoch-stamped stems — [artifacts.md](artifacts.md)).
2. Challenge (consumers use **keep** only).
3. Fix per [fix-routing.md](fix-routing.md) (`outcome: fix` required).
4. Re-assess / evaluate exit rules below.
5. Overwrite `REVIEW_DIR/report.md` each epoch.

Re-enter fix routing after a non-clear epoch when `n < max_epochs` — see [fix-routing.md](fix-routing.md).

## Clear report (success)

After Challenge on the latest assess:

| Decision | Condition |
|----------|-----------|
| **`pass`** | Zero `keep` rows in **all** lanes (code, test, security) |
| **`warnings`** | Zero `keep` in **code** and **test**; one or more security-only `keep`s remain (unfixable) |

Either outcome is **endless exit success** — orchestrate may set `step_review_done: true`.

Security-only `keep`s are **not** fixable under `--fix`; do not burn epochs trying to clear them.

## Exit rules (after each Challenge / re-assess)

Evaluate **OR**:

1. **Clear / pass** — zero `keep` all lanes → exit success, decision `pass`.
2. **Warnings-security-only** — code+test clear; security keeps remain → exit success, decision `warnings`.
3. **Epoch cap** — current epoch equals `--max-epochs` (default 5) and neither (1) nor (2) → stop; do **not** set `step_review_done`; orchestrate hard-stops the chain.

## Hard stop (non-success)

| Trigger | Effect |
|---------|--------|
| Incompatible flags / empty allowlist / policy abort | Stop before or during loop; no success exit |
| Assess failed for a lane needed by `--fix` | Skip that lane’s fix; note in report; continue epoch evaluation |
| Unchallenged challengeable rows | **Stopped:** `unchallenged report` |
| Epoch cap without clear/warnings | Leave report with remaining keeps; chat notes max-epochs; orchestrate leaves `step_review_done` unset |

## Chat / report

- Success: announce `Report written: .ai/review/<runId>/report.md` with decision `pass` or `warnings`.
- Cap: same path; decision not pass/warnings-success; note epochs exhausted.
