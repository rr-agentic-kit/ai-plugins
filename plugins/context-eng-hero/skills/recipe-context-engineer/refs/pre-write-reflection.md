# Pre-write reflection (internal)

Mandatory **before pre-ship and write** on paths that use `refs/actions/shared-write-gates.md`. Produces a compact reflection block per `templates/pre-write-reflection.template.md`—not a full `templates/audit-output.template.md` report.

**Prerequisite:** **Static gate** already PASS on the draft at `<relative-path>` (reuse that output—do not re-run static here).

## Ref index (Read at step)

| Ref | When |
|-----|------|
| `failure-patterns.md` | Step 5 (on FAIL) |
| `templates/pre-write-reflection.template.md` | Step 5 |
| `template-required-map.md` | Step 3 (evidence quotes) |
| Type rubric in `rubrics/<type>.rubric.md` | Step 1 (if not loaded this action) |

## Harness guidance (evaluate in step 4)

**Reliable:** Observable done conditions; explicit fail signals (`PRE-SHIP FAILED`, `PRE-WRITE REFLECTION FAILED`); bounded missing-input behavior.

**Consistent:** No contradictory MUST/MUST NOT; same terms across sections; co-loaded refs add unique constraints only.

**Deterministic:** Enumerable choices → AskQuestion; output shape pinned; branches use observable predicates.

## Pre-write harness checks (ids)

| id | Severity | PASS when |
|----|----------|-----------|
| `harness.reliable.done-stop` | critical | Every imperative step in Procedure/Progress has done/stop or cites single-shot N/A in one line |
| `harness.reliable.fail-signal` | critical | Failed gates block write with named failure label; no soft-fail language on ship path |
| `harness.consistent.contracts` | major | Inputs/outputs/stop rules align across frontmatter description, contracts, and body |
| `harness.consistent.no-cross-echo` | major | Artifact body does not restate constraints already present in files it loads; co-loaded refs do not duplicate each other |
| `harness.deterministic.inputs` | major | Missing required input behavior is explicit; enumerable forks use AskQuestion or fixed options |
| `harness.deterministic.output` | major | Success/failure outputs are verifiable without rereading the whole repo |
| `harness.deterministic.branches` | major | If/else branches use observable conditions; no unbounded discretion on ship path |

## Procedure

### 1. Type and rubric

- **Outcome:** Artifact type and rubric are loaded.
- **Done when:** Path read; type stated; rubric file read from `rubrics/<type>.rubric.md` (Skill+Ref: also `rubrics/skill-ref.rubric.md`).

### 2. Deep reflect (mandatory narrative, brief)

Before scoring rows, write four bullets (in the reflection output or immediately above tables):

1. **Invoker simulation** — minimal valid input; what the executor does first.
2. **Failure modes blocked** — what bad behavior this artifact must prevent.
3. **Ambiguity scan** — any step or branch two competent agents could interpret differently (cite line or heading if found).
4. **Redundancy scan** — any section that restates a constraint from a ref this artifact loads (cite file + line if found).

If ambiguity scan is non-empty, treat related rubric/harness rows as FAIL until the draft is revised. If redundancy scan is non-empty, treat `harness.consistent.no-cross-echo` as FAIL.

### 3. Judgment evaluation

- **Outcome:** Every **Judgment** row in the type rubric is PASS/FAIL with quoted evidence per `template-required-map.md`.
- **Done when:** Same rules as `audit-3-judgment`; do not manually rescore static ids unless script was SKIPPED.

### 4. Harness evaluation

- **Outcome:** Every harness row above is PASS/FAIL with evidence.
- **Done when:** All `harness.*` ids evaluated.

### 5. Merge and verdict

- **Outcome:** Reflection block emitted; pass/fail known.
- **Done when:** Output matches `templates/pre-write-reflection.template.md`; **PASSED** only if all judgment + harness rows PASS.

### 6. On FAIL

- Map FAIL ids to `failure-patterns.md` labels.
- Apply **minimal** edits to the draft (same scope as the hosting action).
- **Do not write.** Re-run **Static gate** → this procedure → **Pre-ship gate**.

## Stop

- Do not skip reflection because pre-ship will run later—reflection owns rubric depth; pre-ship owns binary orchestration/safety/discovery.
- Do not write the target file while result is **FAILED**.
