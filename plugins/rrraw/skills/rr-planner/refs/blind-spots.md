# blind-spots

**Owner:** Blind-spot taxonomy, alternatives analysis, comparison tables, and devil's-advocate patterns for challenge phase.

**Load when:** `--challenge` / `--review` action or challenge agent invocation.

## Blind-spot taxonomy

| Category | What to look for |
|----------|------------------|
| **Stakeholder gaps** | Missing personas, ignored detractors, internal vs external users |
| **Failure modes** | Error paths, rollback, degradation, data loss scenarios |
| **Non-functional** | Security, privacy, compliance, performance, accessibility, i18n |
| **Operational** | Support burden, monitoring, on-call, migration, deprecation |
| **Competitive** | Incumbent alternatives, build-vs-buy, switching costs |
| **Economic** | Hidden costs, revenue model gaps, unit economics |
| **Temporal** | Sequencing risks, dependency chains, MVP scope creep |
| **Assumption debt** | Unvalidated assumptions treated as facts |
| **Traceability breaks** | FRD reqs with no PRD goal parent |
| **Negative space** | What is explicitly out of scope and why |

## Alternatives analysis

For each major decision or requirement:

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

Apply systematically across all loaded docs:

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

## Challenge output expectations

Challenge agent must:

1. Scan all docs in scope against full taxonomy.
2. Produce at least one finding per doc (or explicit `no_findings` with justification).
3. Include comparison table when docs recommend a single approach without alternatives.
4. Never modify docs — findings only; user re-runs `--discover` to apply fixes.
