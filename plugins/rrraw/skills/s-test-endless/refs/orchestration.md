# Add-test perfection orchestration (loop index)

**Product spec:** [README.md](../README.md)

**Mechanical parity:** Shared blocks in [`orchestration-core.md`](orchestration-core.md). Phase mechanics in [`phases/`](phases/).

**Audience:** **`s-test-endless`** orchestrator (depth 0) for **`rr-builder --add-endless-test`** only. **Do not** load inside nested subagents.

**Canonical split:** **`prompts.md`** = Task bodies; **`orchestration-core.md`** = callbacks + load bundles; **this file** = loop index + entry slice; **phase refs** = § mechanics.

---

## Prerequisites

1. **`REPO_ROOT`** — absolute path to repository under review.
2. **`Scope:`** — first substantive prompt line.
3. **`PLUGIN_ROOT`** — installed **rrraw** plugin root.
4. **Initial coverage gateway** — iteration **`n = 1`**: command already ran gateway; **skip §0**. **`n > 1`**: run **`phases/coverage.md`** before §1.
5. **`Start:`** — **`fresh`** | **`plan`** | **`execute`** per **`input-resolution.md`**.

**Violations:** missing **`Scope:`** or **`PLUGIN_ROOT`** → **Stopped:** per **`terminal-report.md`**.

---

## Your role

Add-test perfection orchestrator. Execute loop per **Entry slice** until **`exit-conditions.md`** or budget exhaust.

**Do not** edit application/test code — **`orchestration-core.md`** orchestrator role.

**Chat progress:** **`TodoWrite`** per **SKILL.md** — independent of §3b manifest.

---

## Entry slice (`Start:`)

| **`Start:`** | Run this iteration |
|----------------|-------------------|
| **`fresh`** | §0 (if **`n > 1`**) → §1 → §9 via phase refs |
| **`plan`** | Skip §1. Aggregate from checkpoint/disk → §2 → §3+ |
| **`execute`** | Skip §1–§3. §4 queue from **Glob** → §6 → §7 |

**Checkpoint after §1 (`Start: fresh`):** write **`assessment_paths_by_chunk`** per **`artifacts.md`**.

---

## Loop (`--max-epochs`, default 5)

Outer iteration **`n`** (1-based). One iteration = phases below honoring **Entry slice** skips.

| § | Phase ref | Summary |
|---|-----------|---------|
| 0 | [`phases/coverage.md`](phases/coverage.md) | Toolchain gateway (`n > 1` only) |
| 1 | [`phases/assess.md`](phases/assess.md) | Exhaustive assess per chunk |
| 2 | [`phases/assess.md`](phases/assess.md) | Exit check on assess |
| 3 | [`phases/plan.md`](phases/plan.md) | Planner per chunk |
| 3a | [`phases/plan.md`](phases/plan.md) | Packing gate (helper) |
| 3b | [`phases/plan.md`](phases/plan.md) | Main-chat manifest (helper) |
| 4–6 | [`phases/execute.md`](phases/execute.md) | Queue, progress, dispatch |
| 7 | [`phases/verify.md`](phases/verify.md) | Build + test verify |
| 8 | [`phases/assess.md`](phases/assess.md) | Re-assess |
| 9 | [`phases/verify.md`](phases/verify.md) | Budget / clean exit |

**Callback extensions (orchestrator-only):** multi-chunk assess aggregate — see **`phases/assess.md`**; base shapes in **`orchestration-core.md`**.

---

## Flaky / quarantine

Per **test-heuristics.md**; list under **Remaining gaps**; not clean exit unless policy allows.

---

## Report

Terminal block from **`terminal-report.md`**: **`Test review complete`**, **`Stopped:`**, or **`Deferred:`**.

---

## Hard stops

Per **exit-conditions.md** — **`Stopped:`** shape from **terminal-report.md**.

---

## Delegation discipline

- **Never** implement tests or production fixes in the command runner — only **`Task`** to **`test-endless-assess`**, **`test-endless-plan`**, **`test-endless-fix`**, **`test-endless-toolchain`**.
- **Never** spawn a nested orchestrator subagent.
- **Success** terminal = **`Test review complete`** only.
- Merge conflicts: worker resolves; unresolved after retry → hard stop.

---

## Parameters

Honor **`Scope:`**, **`Start:`**, **`--max-epochs`**, **`--max-parallel`**, checkpoint (**`artifacts.md`**), and **`$ARGUMENTS`** in subagent prompts.

**Forbidden:** **`--skip-plan`**, **`--skip-assess`**, **`--phase=…`**, **`--max-plans`**, or flags that reorder §1→§7 outside documented **`Start:`** slices.
