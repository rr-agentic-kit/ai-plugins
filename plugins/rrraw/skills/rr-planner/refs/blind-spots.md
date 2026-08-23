# blind-spots

**Owner:** Global blind-spot taxonomy, per-level applicability, alternatives analysis, and devil's-advocate patterns.

**Load when:** Stage-exit (skill-inline, **this level's row** only) **and** `--challenge` / `--review` (challenge agent, **union** of all rows).

Do not copy this taxonomy into [doc-standards/](doc-standards/). Those files own required sections and done-when. Each standard points at its applicability row.

## Skill-inline vs agent

| Path | Who | Scope | Output |
|------|-----|-------|--------|
| Stage-exit | Skill (inline, not `Task`) | `in_scope` + `inherit_check` for the current cascade level | Findings merged via re-compose or recorded as assumptions; **no** per-level `challenge-report` |
| `--challenge` | Challenge agent | **Union** of every row (full taxonomy) across all loaded docs | `challenge-report.md` |

Do **not** spawn the challenge agent per level. Alternatives analysis only for major decisions **in scope at that level**.

### Stage-exit rules

- One pass per level against that row.
- `critical` / `high` → questioning ([goal-anchor.md](goal-anchor.md)) before freeze.
- **Premise-critical** (`economic` sizing, obtainable share, "what must be true", unit-economics hurdle on a Must / `must-correct`) → escalate into **Gate 7**, not a medium assumption. Sit the level's roster ([expert-panel.md](expert-panel.md)).
- `medium` / `low` → assumptions / open questions; do not block unless the user wants them.
- User may explicitly accept remaining findings. User may not silently accept a premise-critical finding — it becomes Gate 7.
- Findings that belong in the doc merge via re-compose.
- Skip static ref/id findings when `validate_planning.sh` already ran.

### Challenge rules

- Scan the union across all loaded docs.
- Skip static ref/id findings when `validate_planning.sh` ran.
- Write `challenge-report` only on `--challenge` / `--review`.

## Blind-spot taxonomy

One catalog. Category ids are the keys used in the applicability matrix.

| Category id | What to look for | Persona (seat) |
|-------------|------------------|----------------|
| `stakeholder_gaps` | Missing personas, ignored detractors, internal vs external users, hidden approvers | domain-practitioner, UX |
| `failure_modes` | Error paths, rollback, degradation, data loss scenarios | SRE/QA, staff-engineer |
| `non_functional` | Security, privacy, compliance, performance, accessibility, i18n | SRE/QA, staff-engineer |
| `operational` | Support burden, monitoring, on-call, migration, deprecation, internal system dependencies | COO, SRE/QA |
| `competitive` | Incumbent alternatives, build-vs-buy, switching costs | CMO, growth-investor |
| `economic` | Hidden costs, revenue model gaps, unit economics, cost of inaction, sizing proxies, TAM/SAM/SOM or internal hours×cost | growth-investor, CFO |
| `temporal` | Sequencing risks, dependency chains, why-now, approval timing, posture (existence × commitment), cut-pass vs legend, Must inflation under `signed_v1` | founder/CEO, seed-investor |
| `assumption_debt` | Unvalidated assumptions treated as facts | seed-investor, domain-practitioner |
| `traceability_breaks` | Judgment: compound leaves, inflated MoSCoW, untestable shalls, **current-level facts that belong in another doc** (should have been a note session). Static parent/id failures come from `validate_planning.sh` — do not re-score if the script ran. Requirement-explosion overflow routes to `tech.md`. | head-of-product, staff-engineer |
| `negative_space` | What is explicitly out of scope and why | founder/CEO, head-of-product |

## Applicability matrix

Stage-exit scans **only** `in_scope` + `inherit_check` for the current level. `defer` lenses must not fire at this stage (no premature PRD detail at exec-summary; no "N/A" skip of an in-scope lens). `--challenge` ignores this restriction and uses the union.

| Level | `in_scope` | `inherit_check` | `defer` |
|-------|------------|-----------------|---------|
| **exec-summary** | `negative_space`; `temporal` (why now **and** posture); `economic` (cost of inaction); `stakeholder_gaps` (who feels the pain); `assumption_debt` | — | Competitive detail → MRD. System failure modes, NFR, operational → PRD when in-scope-as-product-commitment, else `tech.md` |
| **mrd** | `competitive`; `economic` (sizing proxies); `stakeholder_gaps` (buyer vs user); `temporal` (trends vs why-now); `assumption_debt` | Exec-summary non-goals still hold | Failure modes, NFR, operational → PRD when in-scope-as-product-commitment, else `tech.md` |
| **brd** | `stakeholder_gaps` (hidden approvers); `economic` (objectives); `operational` (internal dependencies); `temporal` (approvals); `assumption_debt` | Do not re-litigate MRD landscape | Failure modes, NFR, product Won't → PRD when in-scope-as-product-commitment, else `tech.md` |
| **prd** | `failure_modes`; `non_functional`; `operational` (monitoring/migration); `negative_space` (product Won't); `temporal` (cut-pass vs posture legend; Must inflation under `signed_v1`; shipped-as-Must under `existing`); `stakeholder_gaps` (personas vs BRD); `traceability_breaks` (compound stories; facts that belong in another doc; requirement-explosion → `tech.md`); alternatives on major features | Personas/objectives vs BRD; competitive/economic only for **contradiction** with upper levels — no new market debate | Mechanism-level detail (integration points, error-handling specifics, AC overflow) → `tech.md` |

## Alternatives analysis

For each major decision or requirement **in scope at the current level** (stage-exit) or across loaded docs (`--challenge`):

1. **Name 2–3 alternatives** including "do nothing" where applicable.
2. **Compare** on: effort, risk, time-to-value, reversibility.
3. **State recommendation** with rationale tied to stated goals.
4. **Flag** if docs present only one option without justification.

### Comparison table format

```markdown
| Option | Effort | Risk | Time-to-value | Reversibility | Fit to goal |
|--------|--------|------|---------------|---------------|-------------|
| A: ... | Low | Med | Fast | High | Strong |
| B: ... | ... | ... | ... | ... | ... |
```

## Devil's-advocate prompts

Apply on `--challenge` across all loaded docs. At stage-exit, apply only when the prompt maps to an in-scope or inherit_check category for that level.

| Lens | Question |
|------|----------|
| Inversion | "How would we guarantee this fails?" |
| Stakeholder | "Who would veto this and why?" |
| Scale | "What breaks at 10x users/data/teams?" |
| Simplicity | "What can we remove and still meet the goal?" |
| Evidence | "Which claims have no supporting fact or assumption id?" |
| Dependency | "What external factor kills this if it changes?" |

## Severity classification

| Severity | Criteria |
|----------|----------|
| `critical` | Blocks shipping or violates stated goal; no mitigation documented |
| `high` | Significant risk; mitigation missing or weak |
| `medium` | Gap or weak traceability; workaround likely exists |
| `low` | Enhancement, clarity, or minor omission |

## Finding format

```json
{
  "id": "bs-001",
  "category": "failure_modes",
  "severity": "high",
  "doc_ref": "prd.md § 3.2",
  "finding": "No rollback strategy for failed migration",
  "evidence": "PRD describes migration but no failure/revert path",
  "recommendation": "Add rollback acceptance criteria or defer migration to v2",
  "alternatives": []
}
```

`doc_ref` uses the `.md` filename.

## Static vs judgment

[success-criteria.md](success-criteria.md). Judgment only: compound leaves, MoSCoW inflation vs the posture legend, vague AC, missing/wrong posture, off-level facts sitting on the wrong doc.

## Challenge output expectations

Challenge agent must:

1. Scan all docs in scope against the **union** of the taxonomy (judgment).
2. Produce at least one finding per doc (or explicit `no_findings` with justification).
3. Include comparison table when docs recommend a single approach without alternatives.
4. Never modify docs — findings only; user re-runs `--discover` to apply fixes.
5. Do not re-check parent pointers, ID density, or spec gates when the validator ran.
