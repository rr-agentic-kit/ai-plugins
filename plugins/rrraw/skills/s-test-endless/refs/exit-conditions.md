# Endless add-test: canonical exit conditions

Single source of truth for when the **endless add-test** loop stops iterating and emits the terminal report. Loaded by `orchestration.md`, `terminal-report.md`, and `README.md`.

**Default `--max-epochs`:** **5** (this lane; s-review test fix defaults **3**).

---

## Disjunctive vs conjunctive (read this first)

- **Between** numbered **success exit** rules **1–3** below, logic is **OR (disjunctive)**: evaluate after each **assess** or **re-assess**; **exit the loop** when **any one** of 1, 2, or 3 is satisfied (unless a **hard stop** applies first).
- **Inside** rule **2** only, logic is **AND (conjunctive)**: **coverage ≥ target** and **no critical gaps** must **both** hold.

```text
exit_loop ← (1) ∨ (2a ∧ 2b) ∨ (3)

(1)  no remaining gaps (subject to flaky/quarantine rules)
(2a) coverage ≥ target
(2b) GAP ANALYSIS has no critical gaps
(3)  iteration == --max-epochs (default 5)
```

---

## Success exit rules (after each assess or re-assess)

1. **No gaps** — **`COUNTS:`** defect verdict counts are **zero** per project policy (typically **`MISSING`**, **`NON-COMPLIANT`**, **`UNCLEAR`**, and often **`OVER-TESTED`** all **0**). See `assess-output.md` and `test-heuristics.md` for flaky/quarantine exceptions.

2. **Coverage and critical-gap gate** — **Coverage ≥ target** (per project policy; scope from toolchain / `project-detection.md`) **and** **GAP ANALYSIS** has **no critical gaps** (untested business logic, missing layers, or assertion-quality collapse per `test-heuristics.md` and `assess-output.md`).

3. **Iteration cap** — Current iteration equals **`--max-epochs`** (default **5**).

**Quality-only signals** (mutation score, assertion mix) **do not** satisfy an exit rule by themselves unless the project explicitly elevates them.

---

## Hard stops

Stop the workflow and report; **do not** claim a successful improvement loop:

- No test framework detected (pre-flight).
- Unrecoverable **`Task`** failure.
- Merge conflict the subagent cannot resolve after retry.
- Executor failure after retries.
- Explicit **Stopped:** from policy (trunk branch, missing **`PLUGIN_ROOT`**, packing gate, etc.).

On **hard stop**, emit **`Stopped:`** per `terminal-report.md`. On **success exit**, emit **`Test review complete`** per the same template.
