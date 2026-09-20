# Work-pack sizing (plan-agent-owned)

**Audience:** **`test-endless-plan`** (`STAGE=plan`) — **Load first** per agent file. You **pack** designed steps into **one or more** plan markdown files (**work-packs**) under **`REVIEW_DIR/plans/`** before the fix-flow runner dispatches worker **`Task`**s. The **orchestrator** does **not** re-score steps, re-split packs, or merge batches; it only **reads** your artifacts and **dispatches** fixers per pack frontmatter + step status.

**Optional (orchestrator):** One-line sanity check only — if a plan file is missing `pack_sequence` when siblings exist, or `sequential_after` references an unknown path, **stop** and **Report**; do not “fix” packing in the runner.

---

## Goals

- Each **work-pack** (default: **one** **`REVIEW_DIR/plans/trp-*.md`** file) maps to **one** fix **`Task`** with **all steps in that file** executed **in list order**, staying **≤ `HARD_MAX`** abstract **context units** (rubric below).
- **Pack purpose:** Bound **one worker `Task`** subagent context. Fill each pack toward **`HARD_MAX`** with steps that **must** serialize (file collision).
- **Determinism:** Same assessment + same rubric + same packing rules → same file boundaries and frontmatter fields (stable **`pack_sequence`**, explicit edges).
- **Mixed kinds:** A pack may contain **code**, **test**, and **security** steps — packs are **not** “a code pack and a test pack.”

---

## Product principles (packing)

| Principle | Rule |
|-----------|------|
| **Collision → same pack** | Steps sharing any **`target_file`** or **mutex** requiring non-interleaved edits on the same file **belong in the same pack**, executed sequentially in step order. |
| **Move to next pack — only reason** | A step moves to the **next pack-stage** iff it **does not fit** `HARD_MAX` in the current pack **and** its file set is **disjoint** from the current pack’s file set. |
| **Collision + overflow** | If a step **collides** with the current pack but **does not fit**: **re-bin** — move a **larger disjoint chunk** out of the current pack to make room; **do not** push the colliding step to a later pack. |
| **Oversize single step** | If **one step alone** exceeds **`HARD_MAX`** → dedicated pack with **`packing_exception: oversize_step`**; **`HARD_MAX` is waived** for that pack (only allowed exception). |
| **Mixed fill** | A pack may contain one **large** step plus **smaller disjoint steps** in the **remaining** rubric headroom. |
| **Parallelism** | Packs in the same ready layer with **pairwise disjoint** file sets run in parallel, capped by orchestrator **`--max-parallel`**. |

---

## Work-pack = plan file (default)

- **One plan file** = **one work-pack** = **one** worker **`Task`**, **`## Steps`** section = ordered step list for that **`Task`**.
- **Multiple files** = multiple **`plan_path`** values; the runner builds its queue **only** from your YAML frontmatter (**no** runner-side greedy batching).
- **Anti-pattern:** Do **not** emit many tiny plan files when **one** merged file would stay **≤ `HARD_MAX`** with collision rules preserved.

---

## Context unit rubric (deterministic)

Values are **not** tokenizer counts; they are **planner scores** for **sizing and splitting**. **Sum** scores of **steps you place in a candidate file**; then add **deduplicated path overhead** for that file.

### 1) Steps to score

Treat each planned **step** (checkbox line + continuations) with:

- **action** (`create` / `update` / `delete` / `refactor` / `harden`)
- **kind** (`code` / `test` / `security`) — from assessment lane; default **code** when absent
- **test_type** (unit, component, integration, contract, e2e — **test** steps only; normalize lowercase; unknown → **integration**)
- **target_file** (backtick path on the step line)
- **mutex** label if present
- **risk** from continuations: `risk:\s*(low|medium|high)`; default **medium** if absent

### 2) Per-step base score (sum into file total)

| Action | Add (units) |
|--------|-------------|
| `create` | 12,000 |
| `update` | 9,000 |
| `delete` | 7,000 |
| `refactor` | 11,000 |
| `harden` | 10,000 |

| Kind | Add (units) |
|------|-------------|
| `code` | 8,000 |
| `test` | 5,000 (base; add test_type when present) |
| `security` | 12,000 |

| Test type (normalized; **test** kind only) | Add (units) |
|--------------------------------------------|-------------|
| `unit` | 5,000 |
| `component` | 8,000 |
| `integration` | 15,000 |
| `contract` | 16,000 |
| `e2e` | 22,000 |
| (unknown) | 12,000 |

| Risk | Add (units) |
|------|-------------|
| `low` | 6,000 |
| `medium` | 10,000 |
| `high` | 18,000 |

**Step total** = action + kind + (test_type when kind=test) + risk.

### 3) Deduplicate paths inside one **file**

- Collect **target_file** from every step in that file; optionally add path-like tokens from **`Traces:`** (repo-relative paths with `/` and plausible extensions).
- **Per unique** path in that file, add **8,000** units once.

**File score** = (sum of step totals in file) + (8,000 × unique paths). Echo as YAML **`estimated_context_units: <int>`** — **recommended** on every file.

**Constants**

- **`SOFT_MIN`** = 80,000 — **lint only** (orchestrator may warn on under-filled packs); **not** a packing target.
- **`HARD_MAX`** = 120,000 — **no** delivered plan file’s rubric total may exceed **`HARD_MAX`** except **`packing_exception: oversize_step`** (single step > **`HARD_MAX`**).

---

## Packing algorithm (canonical — numbered)

1. **Collision graph:** Connect steps sharing any **`target_file`** (create/update/delete) or **mutex** requiring non-interleaved edits on the same file. Each connected component is an **ordered sequence** — **never** split colliding steps across packs.

2. **Bin-pack within a component:** Walk ordered steps; add to current pack while `rubric_sum ≤ HARD_MAX`. After placing a large step, add any **later** steps whose file sets are disjoint-within-pack and still fit (**mixed fill**).

3. **Overflow — disjoint:** Current pack full; next step’s files ∩ current pack files = ∅ → **new pack-stage**.

4. **Overflow — colliding:** Next step must stay with colliding peers but does not fit → **re-bin**: identify the **largest disjoint subsequence** (or single large step) in the current pack that can move to a new pack without breaking collision rules; retry placement. **Never** satisfy overflow by moving a colliding step to a later pack.

5. **Oversize step:** If one step’s rubric **`> HARD_MAX`** and cannot be decomposed → one pack, that step only, **`estimated_context_units`** = actual score, **`packing_exception: oversize_step`**.

6. **Cross-pack parallelism:** After all packs emitted, packs whose **full file sets** (all **`target_file`** + relevant **`Traces:`** paths) are **pairwise disjoint** may share a **parallel layer**. Set matching **`parallel_group`** on siblings; orchestrator **verifies** disjointness.

---

## Mutex / order

- Steps sharing a **mutex** label must **not** be edited in an interleaved way across **concurrent** workers — same pack **or** **`sequential_after`** so only one runs at a time.
- **Never** reorder steps vs your design: preserve assessment-derived step order across **`sequential_after`** chains.
- **Cross-file:** use **`sequential_after`** (repo-relative paths to **other** plan files) so the runner never guesses order.

---

## YAML frontmatter

### Base keys (every file)

```yaml
---
title: Review remediation plan
type: review-plan
complexity: <small|medium|large>
status: active
date: YYYY-MM-DD
assessment_refs: [<paths to assess artifacts from this round>]
branch_prefix: review-fix/<short-branch>
branch: review-fix/<short-branch>/pack-<NN>
pack_sequence: <int; 1 for single-file>
sequential_after: [<repo-relative paths to other plan files from this invocation, or empty list>]
estimated_context_units: <int>
target_files: [<denormalized target_file + key Traces paths>]
---
```

Omit **`parallel_group`** on single-file output; omit **`packing_exception`** unless **`oversize_step`** or **`natural_tail`** applies.

### Multi-file requirements (N > 1)

When this invocation emits **more than one** plan file:

- **Every** file includes all **Base keys** above; **`pack_sequence`** and **`sequential_after`** are **required** on each file (empty **`sequential_after`** only when that file has no intra-chunk predecessors).
- **`parallel_group`:** set the same non-empty value only on siblings in the same ready layer with **pairwise disjoint** file sets (orchestrator verifies; subject to **`--max-parallel`**).
- **`packing_exception`:** set **`oversize_step`** or **`natural_tail`** when § Packing algorithm applies; otherwise omit.

**Single-file output:** **`pack_sequence: 1`**, **`sequential_after: []`**.

### Execution state (optional YAML — not packing)

| Key | Type | Semantics |
|-----|------|-----------|
| **`last_worker_run`** | string (ISO-8601) | UTC timestamp of last successful worker **`Task`**. |
| **`execution_status`** | string | **`pending`**, **`in_progress`**, or **`done`**. |
| **`last_updated`** | string (ISO-8601) | Optional. |

**Step line progress** (`- [executed]` / `- [verified]`) in **`## Steps`** is the **authoritative** progress signal — see **`skills/rr-builder/rr-test-endless/refs/orchestration.md`** §5.

---

## Plan body (canonical)

```markdown
## Goal
…

## Integrity check
PASS | CONFLICT — …

## Steps

Steps execute **in list order** in one worker **`Task`**. Mutex labels separate targets that must not be interleaved; they do **not** imply parallel execution inside one **`Task`**.

- [ ] **Step 1** | <action> | kind: <code|test|security> | <test_type if kind=test> | `<target_file>` | mutex: <group> | risk: <low|medium|high>
  Verify: <how fixer marks [verified]>
  …
  Traces: …

## Excluded
…
```

**Step status (SoT for resume):**

- `- [ ]` — pending (fixer may claim this pack’s next pending step)
- `- [executed]` — change applied; verify not done (resume starts at verify)
- `- [verified]` — oracle / scoped tests / toolchain for that step passed (terminal)

---

## Completeness (planner gates)

- **Every** kept finding (all lanes) is covered across **all** pack files (steps or **Excluded**).
- **No** pack file exceeds **`HARD_MAX`** except **`oversize_step`**.
- **Collision:** No colliding steps split across packs.
- **`sequential_after`** references only paths you wrote in this invocation.
- Final chat lists **all** paths per **`orchestration-core.md`** § Callback contracts (Planner).

## See also

- **`agents/test-endless/plan.md`** — workflow phases; **`PACKING_RETRY:`** / **`PARALLEL_RETRY:`** from **`orchestration.md`** §3a.
- **`skills/rr-builder/rr-test-endless/refs/orchestration.md`** / **`orchestration.md`** §4 — queue from planner artifacts; **`--max-parallel`**.
- work-pack sizing in this ref — Plan spec (canonical).
