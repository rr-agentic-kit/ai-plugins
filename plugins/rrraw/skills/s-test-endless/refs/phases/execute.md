# Phase: execute (§4, §5, §6)

**Load bundle:** execute (see **`orchestration-core.md`**).

## §4 Read plans and build execute queue

**Work-pack** = **one** `plan_path`. Orchestrator does **not** re-pack.

**`--max-parallel`:** From **`$ARGUMENTS`**; default unlimited. Non-positive → **Stopped:** **`policy`**.

**`Start: execute`:** **`Glob`** **`REVIEW_DIR/plans/trp-*.md`**; build queue from all matches.

**Otherwise:** use plan paths from §3 / §3a retry output.

Build queue via helper:

```bash
python3 scripts/endless_test_helpers/cli.py dispatch-queue --plans-dir <dir> [--max-parallel N]
```

Stdout: JSON layers with **`plan_path`**, **`branch_name`**, **`pack_sequence`**, **`parallel_batch`** indices. On intersecting file sets in a concurrent batch → helper exits non-zero → **Stopped:** **`packing_gate`**.

**In-memory queue** = helper output. **§5** plan markdown remains completion SoT; checkpoint **`completed_plan_paths`** is resume-only (**`artifacts.md`**).

## §5 Progress on plan files

**Source of truth:** **`REVIEW_DIR/plans/trp-*.md`**. **`test-endless-fix`** (or depth-0 runner) **Edit**s checkboxes and optional execution YAML after **`{ "success": true }`**.

## §6 Execute (per work-pack)

### §6.0 Checkpoint

Schema and field meanings: **`artifacts.md`** § Checkpoint JSON — **do not** duplicate the field table here.

**Path:** **`REVIEW_DIR/test/state/endless-add-test-checkpoint.json`**

**Resume playbook:**

1. **`Read`** checkpoint; confirm **`iteration_n`** + **`scope`** match current run. **Path-consistency probe:** if checkpoint paths (**`assessment_paths_by_chunk`** values, **`completed_plan_paths`**) are not under the current **`REVIEW_DIR`** (e.g. run dir was moved/renamed), warn once and treat the checkpoint as resume-only telemetry — plan files remain SoT.
2. Rebuild §4 queue (helper); drop **`completed_plan_paths`**; also drop packs whose plan YAML shows **`execution_status: merged`** or all steps **`[verified]`** (pre-dispatch resume sweep — checkpoint may be stale; helper **`--skip-merged`** when supported).
3. Dispatch **`test-endless-fix`** for remaining layers.
4. On each success, append **`plan_path`**, **`Write`** checkpoint, apply §5.
5. Queue empty → **§7 verify** → **§8–§9** or advance **`n`**.

### §6.1 Dispatch-until-empty

Continue all layers until queue empty → **§7**. **`Deferred:`** only on actual host turn end / **`Task`** refusal — not wall-clock or pack count heuristics.

**Dispatch:** **`test-endless-fix`** per layer/batch; one **`Task`** = one work-pack. Dispatch the whole parallel layer in one turn up to **`--max-parallel`** (unlimited default) — do not split a layer into ad-hoc waves.

On **`{ "success": false }`** → **Report** unless retry policy applies.
