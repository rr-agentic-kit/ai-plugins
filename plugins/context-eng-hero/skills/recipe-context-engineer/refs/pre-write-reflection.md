# Pre-write reflection (internal)

Mandatory **before pre-ship and write** on paths that use `refs/actions/shared-write-gates.md`. Produces a compact reflection block per `pre-write-reflection.template.md`—not a full `audit-output.template.md` report.

**Prerequisite:** **Static gate** already PASS on the draft at `<relative-path>`.

## Load (Read)

- `failure-patterns.md`
- `harness-effectiveness.md`
- `pre-write-reflection.template.md`
- Rubric for detected type: `skill.audit-rubric.md` | `command.audit-rubric.md` | `agent.audit-rubric.md` | `rule.audit-rubric.md` | `workflow.audit-rubric.md`

## Procedure

### 1. Type and rubric

- **Outcome:** Artifact type and rubric are loaded.
- **Done when:** Path read; type stated; rubric file read.

### 2. Deep reflect (mandatory narrative, brief)

Before scoring rows, write four bullets (in the reflection output or immediately above tables):

1. **Invoker simulation** — minimal valid input; what the executor does first.
2. **Failure modes blocked** — what bad behavior this artifact must prevent.
3. **Ambiguity scan** — any step or branch two competent agents could interpret differently (cite line or heading if found).
4. **Redundancy scan** — any section or paragraph that restates a constraint from a ref this artifact loads or that a co-loaded ref already covers (cite file + line if found).

If ambiguity scan is non-empty, treat related rubric/harness rows as FAIL until the draft is revised. If redundancy scan is non-empty, treat `harness.consistent.no-cross-echo` as FAIL.

### 3. Judgment evaluation

- **Outcome:** Every **Judgment** row in the type rubric is PASS/FAIL with quoted evidence.
- **Done when:** Same rules as `audit-3-judgment` in `refs/actions/audit.md`; do not manually rescore static ids from script output unless script was SKIPPED.

### 4. Harness evaluation

- **Outcome:** Every row in `harness-effectiveness.md` **Pre-write harness checks** table is PASS/FAIL with evidence.
- **Done when:** All `harness.*` ids in `harness-effectiveness.md` **Pre-write harness checks** evaluated.

### 5. Merge and verdict

- **Outcome:** Reflection block emitted; pass/fail known.
- **Done when:** Output matches `pre-write-reflection.template.md`; **PASSED** only if all judgment + harness rows PASS; top patterns listed for any FAIL.

### 6. On FAIL

- Map FAIL ids to `failure-patterns.md` labels.
- Apply **minimal** edits to the draft (same scope as the hosting action—fix vs redesign vs create).
- **Do not write.** Re-run **Static gate** → this procedure → **Pre-ship gate**.

## Stop

- Do not skip reflection because pre-ship will run later—reflection owns rubric depth; pre-ship owns binary orchestration/safety/discovery.
- Do not write the target file while result is **FAILED**.
