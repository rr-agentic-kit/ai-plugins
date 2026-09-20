# Phase: plan (§3, §3a, §3b)

**Load bundle:** plan (see **`orchestration-core.md`**).

## §3 Plan (single planner per chunk)

If **`Start: execute`**, **skip §3** and **§3a**.

For each **`chunk_id`**, **`Task`** **`test-endless-plan`** per **`prompts.md`** **Plan** section. Parse **`Plan written:`** / **`Plans written:`**; **Read** every plan file.

## §3a Packing quality gate

If **`Start: execute`**, **skip §3a**.

After §3 for each **`chunk_id`**, run:

```bash
python3 scripts/endless_test_helpers/cli.py packing-probes --plans-dir <REVIEW_DIR/plans> --chunk <chunk_id>
```

**Stdout:** probe verdicts (`collision_split`, `collision_overflow`, `micro_packs`, `spurious_sequential`, `parallel_collision`) + optional **`PACKING_RETRY:`** hint line.

- **`parallel_collision`** → **Stopped:** **`packing_gate`** immediately (no retry).
- Other triggering probes → **one** planner retry per **`orchestration.md`** §3a retry rules (append **`PACKING_RETRY:`** line from helper stdout).
- Re-run helper on retry output; still failing → **Stopped:** **`packing_gate`**.

**Skip** when any plan file omits **`estimated_context_units`** (optional field).

## §3b Main-chat work-pack manifest

When **`Start: execute`**, emit a **short** bullet list of **`plan_path`** values (full table optional).

**Otherwise (mandatory):** Before execute phase, run:

```bash
python3 scripts/endless_test_helpers/cli.py manifest-table --plans-dir <dir> --iteration <n>
```

Paste the stdout markdown block into **main agent chat** unchanged (not Shell-only **`echo`**). Canonical shape:

```text
## Endless add-test — iteration <n> / Work-pack dispatch

| pack_sequence | plan_path | branch_name | sequential_after | parallel_group | Grouping (heuristic) |
| --- | --- | --- | --- | --- | --- |
```
