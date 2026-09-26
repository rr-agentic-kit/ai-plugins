# Endless add-test: terminal report template

**Purpose:** Exact markdown shape for **`Test review complete`**, **`Stopped:`**, and **`Deferred:`** terminal lines the orchestrator must emit.

**Exit logic** lives in `exit-conditions.md`. **Loop mechanics** in `orchestration.md`.

---

## Report template (`Test review complete`)

Emit **only** when the loop has exited **cleanly** per **`exit-conditions.md`**:

```
Test review complete
Iterations: X
Steps: Y completed, Z failed
Coverage: before A% → after B%
Mutation score (if run): before P% → after Q%
Assertion quality summary (if assessed): behavioral / trivial / implementation-coupled — [counts or "unchanged"]
Commits: TReview w1/2: …, TReview w2/2: …
Re-assess diff (last iteration): fixed: [n], new: [n], regressed: [n], unchanged: [n] — or "see subagent output"
Quarantined tests (if any): [list with reason / backlog ref; "None"]
Remaining gaps: [list if loop exited at max iterations or with unfixable steps; otherwise "None"]
```

**Optional lines:** omit **`Mutation score`** / **`Assertion quality summary`** entirely when data is unavailable.

---

## Stopped template (hard terminal)

```
Stopped: <reason_code> — <one-line human summary>
Iterations: X (or "n/a" if stopped before first full iteration completed)
Details: [bullet or short paragraph]
Resume: [checkpoint guidance or "None"]
```

### `Stopped:` reason codes

| Code | When to use |
|------|-------------|
| **`toolchain_fail`** | Build or tests did not run / gateway hard fail. |
| **`task_fail`** | Leaf **`Task`** failed twice, JSON parse failure, or missing **`COUNTS:`** after retry. |
| **`packing_gate`** | §3a packing gate failure per `orchestration.md`. |
| **`policy`** | Trunk branch, conflicting scope, missing **`PLUGIN_ROOT`**, invalid flags. |
| **`orchestrator_error`** | Runner bug / inconsistent queue (reserved). |

---

## Deferred template (session-bounded)

**Forbidden `Deferred:` triggers:** wall-clock duration, token forecasts, pack count — while the host accepts **`Task`** and the execute queue is non-empty, continue dispatch per `orchestration.md` §6.1.

```
Deferred: <reason_code> — <one-line human summary>
Phase reached: [e.g. "§3b manifest emitted" / "§6 partial — K of N plan_path dispatched"]
Remaining: [plan_path rows not dispatched / not verified]
Next session: [same flags + resume from REVIEW_DIR/test/state/endless-add-test-checkpoint.json]
```

### `Deferred:` reason codes

| Code | When to use |
|------|-------------|
| **`orchestrator_deferred`** | Host turn ended, **`Task`** refusal, or operator pause before all worker **`Task`**s finished. |

**Contract:** **`Deferred:`** runs should **write or update** `REVIEW_DIR/test/state/endless-add-test-checkpoint.json` per `orchestration.md` §6.0.
