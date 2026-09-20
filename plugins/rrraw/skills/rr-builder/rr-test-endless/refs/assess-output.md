# Assess mode output format (exhaustive)

Use when **`Mode: assess`**. Emit assessment as **markdown only**: a **compact summary block** plus **one defect table** (mode-dependent). Default for review assess Tasks: **`REVIEW_DIR/test/assess/`** per **`review-assess-agent.md`**.

**No JSON output mode.** Downstream (fix orchestration, planners) **Read** the file, parse the **`COUNTS:`** line for exit conditions, and pass **table rows** to the planner.

---

## Two modes (pick one per run)

1. **Live test assess** (`live-assess`) — **Production → coverage.** Walk **production/source** units; ask whether each has adequate test coverage. Subject = production unit. **MISSING** applies here.
2. **Test assess** (`test-assess`) — **Test quality.** Walk **existing test files**; evaluate each test method. Subject = test method. **MISSING** does **not** apply (tests exist).

**Detection:** Caller or prompt names the sub-mode (`live-assess` / `test-assess`) or describes intent (“coverage gaps in production” vs “quality of existing tests”). If unspecified, default to **live-assess** when the walk targets production code; use **test-assess** when scope is test files only or the prompt asks to judge tests.

---

## Shared ground rules

- Walk **every** method/constructor/factory and **every** meaningful branch in scope (**live-assess**: production/source; **test-assess**: test methods). **Vue SFC** (`<script setup>`): method vs branch → **`vue-test.md`**.
- Confront evidence against **`skills/rr-builder/rr-test-endless/refs/test-heuristics.md`** only. **Verdict precedence:** **`Verdict decision matrix`** in `test-heuristics.md`.
- **ADEQUATE** only when **Purpose clarity checklist** (all 4 conditions) holds and no Critical/Major/qualifying Minor path applies — see **`UNCLEAR`** and **Assertion overload** in `test-heuristics.md`.
- **Table = defect list only:** List **only non-ADEQUATE** rows. **ADEQUATE** count appears **only** on the **`COUNTS:`** line (proves exhaustive walk).
- **Target format:** **`<qualified.name>#<symbol>`** — see **Per-finding diagnostic card** in `test-heuristics.md`. **Branch-level:** append **`(branch: <condition>)`** to the target cell (same line, no separate nesting).

**Branches (exhaustive walk):** Error paths, null/empty guards, `catch` blocks, feature flags. Skip only what heuristics mark trivial or out of scope.

Production files with no callables (config-only): still account for the file in **SCOPE** / counts; emit a row only if verdict ≠ ADEQUATE.

**Layer / pyramid / boundary / flow:** Classification rules live in **`test-types.md`**. In **live-assess**, boundary gaps, flow gaps, and layer skew surface as **MISSING** (or other verdicts) **rows** where applicable — not as duplicate prose sections. Optional **LAYERS** line in the summary compresses suite composition.

---

## Summary block (both modes, before the table)

Three required lines (+ optional fourth). When **`BRIEF_PATH`** was consumed, add **GOAL FIT** block **before** **`COUNTS:`**:

```text
GOAL FIT: MET | PARTIAL | MISS | UNRESOLVED
goal_items=N | covered=N | missing=N | extra=N
```

```text
SCOPE: <what was evaluated>
  production_files: N | test_files: N
COUNTS: MISSING=N | NON-COMPLIANT=N | OVER-TESTED=N | UNCLEAR=N | ADEQUATE=N
```

**`COUNTS`:** In **test-assess** mode, always emit **`MISSING=0`** (verdict does not apply). **Do not** drop the **`MISSING=`** token — parsers rely on a stable **`COUNTS:`** shape.

**Optional (live-assess only):**

```text
LAYERS: unit=N integration=N e2e=N | pyramid: <healthy | ice_cream_cone | hourglass | inverted | insufficient_data>
```

**CI-component overlay** — when project kind = **`gitlab-ci-component`** (see `project-detection.md`), use five tokens instead of three:

```text
LAYERS: unit=N k3d=N ci_job=N verify=N e2e=N | pyramid: <healthy | ice_cream_cone | hourglass | inverted | insufficient_data>
```

Application repos use the **three-token** line only. Do **not** emit `k3d`, `ci_job`, or `verify` on application repos.

**Template targets (CI-component live-assess):** Use `templates/<name>/template.yml#inputs.<field>` or `#<job-path>` — not `#method` when the subject is an input or wiring surface.

If mutation score or flaky ratio is known from tooling, add **one** line after **LAYERS** (or after **COUNTS** if **LAYERS** omitted), e.g. `NOTE: mutation_score=82% (PIT)`.

**Cross-lane (live-assess only):** When ≥1 production target cannot get an adequate unit/component test without production edits, add one or more lines after **LAYERS** / **NOTE** and before the table:

```text
BLOCKED (code lane): <paths> | reason: <one line> | remediation: <recipe-id>
```

**`recipe-id`** values: `extract-pure-core`, `introduce-port`, `inject-time`, `thin-boundary` — per [`testability.md`](../../rr-coder/refs/testability.md). Repeat per blocked path when causes differ. Terminal report must list these under **Remaining gaps** / **Blocked (code lane)** per cross-lane escalation section in rr-coder testability ref. Do **not** claim coverage or exit rules met for blocked items.

**Dropped:** **`SUITE_HEALTH`** and **`SUITE_PERFORMANCE`** blocks — suite-level aggregates are derivable from table data and **COUNTS**; optional metrics go in **NOTE** / **LAYERS** only.

---

## Mode 1: Live test assess (production-centric)

**Question:** Is production code adequately tested?

### Table (non-ADEQUATE rows only)

```markdown
| target | verdict | tests | assertion-level | reason | heuristic |
```

| Column | Definition |
|--------|------------|
| **target** | `<qualified.name>#<symbol>`; branch: append `(branch: condition)`. |
| **verdict** | **MISSING** \| **UNCLEAR** \| **NON-COMPLIANT** \| **OVER-TESTED** |
| **tests** | Test references covering this unit: `path::methodName`, comma-separated, or **`none`**. |
| **assertion-level** | **0–4** — strongest oracle among covering tests (**Assertion strength taxonomy** in `test-heuristics.md`). **`-`** when **MISSING** (no tests). |
| **reason** | Brief: why this verdict. **MISSING:** why coverage is required (e.g. “public service method with validation”). **Other:** smell + severity when applicable (e.g. “Full mock chain (Critical): all deps mocked, only verify()”). |
| **heuristic** | Section title from `test-heuristics.md` that drove the verdict. |

---

## Mode 2: Test assess (test-centric)

**Question:** Are existing tests any good?

### Table (non-ADEQUATE rows only)

```markdown
| target | verdict | smell | assertion-level | evidence | heuristic |
```

| Column | Definition |
|--------|------------|
| **target** | `<qualified.name>#<symbol>` — **test method** under verdict. |
| **verdict** | **UNCLEAR** \| **NON-COMPLIANT** \| **OVER-TESTED** (no **MISSING**). |
| **smell** | `Name (severity)` — e.g. `Full mock chain (Critical)`, `Assertion roulette (Major)`. |
| **assertion-level** | **0–4** — strongest oracle in this test. |
| **evidence** | One line — what is wrong (e.g. “5 verify() calls, zero output assertions”). |
| **heuristic** | Section title from `test-heuristics.md`. |

Group rows by test file in prose **above** each table section if it aids readability (optional).

---

## Verdicts (compact reference)

Full definitions, **Purpose clarity checklist**, **Assertion strength** levels, **Severity-classified smells**, and **Verdict decision matrix** live in **`test-heuristics.md`** — do not duplicate here.

| Verdict | Typical use |
|---------|-------------|
| **MISSING** | Live-assess only — should be covered, no adequate test. |
| **OVER-TESTED** | Low/negative value tests per heuristics. |
| **NON-COMPLIANT** | Violates heuristics (Critical/Major, or assertion overload with clear purpose). |
| **UNCLEAR** | Purpose checklist failure or assertion overload with unclear purpose (per matrix). |
| **ADEQUATE** | Not listed in table; counted in **COUNTS** only. |

---

## Re-assess (fix flow)

When comparing to a prior assessment, add a short section after the summary/table:

```text
RE-ASSESS DIFF: <what changed vs prior file or prior pass — new rows resolved, new gaps, verdict shifts>
```

Orchestrators may store the prior assessment **file path** for diffing; no JSON **`reassess_diff`** object.

---

## Downstream parsing (orchestrators)

1. **Read** assessment file as markdown.
2. **Match** `COUNTS: ...` — extract integers for **MISSING**, **NON-COMPLIANT**, **OVER-TESTED**, **UNCLEAR**, **ADEQUATE**.
3. **Parse** markdown table rows (skip header row; ignore separator rows).
4. **Exit conditions** — see **`skills/rr-builder/rr-test-endless/refs/exit-conditions.md`**.

**Multi-chunk runs:** Merge **COUNTS** by summing each verdict column across chunk files; concatenate tables (or merge rows by target key) for planner input.
