# blind-spots

**Owner:** Global blind-spot taxonomy, per-level applicability, alternatives analysis, and devil's-advocate patterns.

**Load when:** Stage-exit (skill-inline, **this level's row** only) **and** `--challenge` / `--review` (challenge agent, **union** of all rows).

Do not copy this taxonomy into [doc-standards/](doc-standards/). Those files own required sections and done-when. Each standard points at its applicability row.

## Skill-inline vs agent

| Path | Who | Scope | Output |
|------|-----|-------|--------|
| Stage-exit | Skill (inline, not `Task`) | `in_scope` + `inherit_check` for the current cascade level | Findings merged via re-compose or recorded as assumptions; **no** per-level `challenge-report` |
| `--challenge` | Challenge agent | **Union** of every row (full taxonomy) across all loaded docs | `challenge-report.md` \| `.yaml` |

Do **not** spawn the challenge agent per level. Alternatives analysis only for major decisions **in scope at that level**.

### Stage-exit rules

- One pass per level against that row.
- `critical` / `high` → questioning ([goal-anchor.md](goal-anchor.md)) before freeze.
- `medium` / `low` → assumptions / open questions; do not block unless the user wants them.
- User may explicitly accept remaining findings.
- Findings that belong in the doc merge via re-compose.
- Skip static ref/id findings when `validate_planning.py` already ran.

### Challenge rules

- Scan the union across all loaded docs.
- Skip static ref/id findings when `validate_planning.py` ran.
- Write `challenge-report` only on `--challenge` / `--review`.

## Blind-spot taxonomy

One catalog. Category ids are the keys used in the applicability matrix.

| Category id | What to look for |
|-------------|------------------|
| `stakeholder_gaps` | Missing personas, ignored detractors, internal vs external users, hidden approvers |
| `failure_modes` | Error paths, rollback, degradation, data loss scenarios |
| `non_functional` | Security, privacy, compliance, performance, accessibility, i18n |
| `operational` | Support burden, monitoring, on-call, migration, deprecation, internal system dependencies |
| `competitive` | Incumbent alternatives, build-vs-buy, switching costs |
| `economic` | Hidden costs, revenue model gaps, unit economics, cost of inaction, sizing proxies |
| `temporal` | Sequencing risks, dependency chains, why-now, approval timing, posture (existence × commitment), cut-pass vs legend, Must inflation under `signed_v1` |
| `assumption_debt` | Unvalidated assumptions treated as facts |
| `traceability_breaks` | Judgment: compound leaves, inflated MoSCoW, weak triad, untestable shalls, **current-level facts that belong in another doc** (should have been a note session). Static parent/id failures come from `validate_planning.py` — do not re-score if the script ran. If skipped, flag `build != none` on non-ready items. |
| `negative_space` | What is explicitly out of scope and why |

## Applicability matrix

Stage-exit scans **only** `in_scope` + `inherit_check` for the current level. `defer` lenses must not fire at this stage (no premature FRD detail at exec-summary; no "N/A" skip of an in-scope lens). `--challenge` ignores this restriction and uses the union.

| Level | `in_scope` | `inherit_check` | `defer` |
|-------|------------|-----------------|---------|
| **exec-summary** | `negative_space`; `temporal` (why now **and** posture); `economic` (cost of inaction); `stakeholder_gaps` (who feels the pain); `assumption_debt` | — | Competitive detail → MRD. System failure modes, NFR, operational → FRD |
| **mrd** | `competitive`; `economic` (sizing proxies); `stakeholder_gaps` (buyer vs user); `temporal` (trends vs why-now); `assumption_debt` | Exec-summary non-goals still hold | Failure modes, NFR, operational → FRD |
| **brd** | `stakeholder_gaps` (hidden approvers); `economic` (objectives); `operational` (internal dependencies); `temporal` (approvals); `assumption_debt` | Do not re-litigate MRD landscape | Failure modes, NFR, product Won't → PRD/FRD |
| **prd** | `negative_space` (product Won't); `temporal` (cut-pass vs posture legend; Must inflation under `signed_v1`; shipped-as-Must under `existing`); `stakeholder_gaps` (personas vs BRD); `traceability_breaks` (compound stories; facts that belong in another doc); alternatives on major features | Personas/objectives vs BRD | NFR targets, error handling, integrations → FRD |
| **frd** | `failure_modes`; `non_functional`; `operational` (monitoring/migration); `traceability_breaks`; `assumption_debt` | Competitive/economic only for **contradiction** with upper levels — no new market debate | — |

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
  "doc_ref": "frd.md § 3.2",
  "finding": "No rollback strategy for failed migration",
  "evidence": "FRD describes migration but no failure/revert path",
  "recommendation": "Add rollback acceptance criteria or defer migration to v2",
  "alternatives": []
}
```

`doc_ref` uses the actual filename extension (`.md` or `.yaml`).

## Static vs judgment

Skill runs `python3 scripts/validate_planning.py <output-dir>` before challenge and as the static half of cascade Gate 3. If the script ran, omit ref/status/drift findings — they are already FAILs. If skipped, include `build` on non-ready / broken parent as findings and record `STATIC SKIPPED`.

Judgment only: compound leaves, MoSCoW inflation vs the posture legend, weak `if_wrong`, vague AC, missing/wrong posture, off-level facts sitting on the wrong doc.

## Challenge output expectations

Challenge agent must:

1. Scan all docs in scope against the **union** of the taxonomy (judgment).
2. Produce at least one finding per doc (or explicit `no_findings` with justification).
3. Include comparison table when docs recommend a single approach without alternatives.
4. Never modify docs — findings only; user re-runs `--discover` to apply fixes.
5. Do not re-check parent pointers, ID density, or spec/build gates when the validator ran.
