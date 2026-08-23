# blind-spots

**Owner:** Global blind-spot taxonomy, per-level applicability, alternatives analysis, and devil's-advocate patterns.

**Load when:** Stage-exit (skill-inline, **this level's row** only) **and** `--challenge` / `--review` (challenge agent, **union** of all rows).

Do not copy this taxonomy into [doc-standards/](doc-standards/). Those files own required sections and done-when. Each standard points at its applicability row.

## Skill-inline vs agent

| Path | Who | Scope | Output |
|------|-----|-------|--------|
| Stage-exit | Skill (inline, not `Task`) | `in_scope` + `inherit_check` for the current cascade level | Findings merged via re-compose or recorded as assumptions; **no** per-level challenge report |
| `--challenge` | Challenge agent | **One target doc** per invocation; **union** taxonomy applied to that doc | Per-doc `{stem}.challenge.report.md` (orchestrator persists) |

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

- One target doc per invocation; scan the union taxonomy on that doc only.
- Skip static ref/id findings when `validate_planning.sh` ran.
- Write per-doc challenge report only on `--challenge` / `--review` (orchestrator persists).

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
| `temporal` | Sequencing risks, dependency chains, why-now, approval timing, posture (existence × commitment), RICE vs posture legend, Must inflation under `signed_v1` | founder/CEO, seed-investor |
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
| **prd** | `failure_modes`; `non_functional`; `operational` (monitoring/migration); `negative_space` (product Won't); `temporal` (RICE vs posture legend; Must inflation under `signed_v1`; shipped-as-Must under `existing`); `stakeholder_gaps` (personas vs BRD); `traceability_breaks` (compound stories; facts that belong in another doc; requirement-explosion → `tech.md`); alternatives on major features | Personas/objectives vs BRD; competitive/economic only for **contradiction** with upper levels — no new market debate | Mechanism-level detail (integration points, error-handling specifics, AC overflow) → `tech.md` |

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
  "doc": "prd",
  "target_doc": "prd",
  "category": "failure_modes",
  "severity": "high",
  "doc_ref": "prd.md § 3.2",
  "finding": "No rollback strategy for failed migration",
  "evidence": "PRD describes migration but no failure/revert path",
  "recommendation": "Add rollback acceptance criteria or defer migration to v2",
  "fix_action": "flag_risk",
  "fix_level": "prd",
  "target_artifact": "doc",
  "paired_finding_id": null,
  "alternatives": []
}
```

| Field | Notes |
|-------|-------|
| `doc` | Cascade stem where the weak spot **appears** (symptom doc). Required. |
| `target_doc` | Cascade stem where the fix belongs. Same as `doc` when inline; differs for dual-stub routing. |
| `fix_action` | Recommended fix type — see enum below. Human confirms before ledger `demote`/`scope_change`. |
| `fix_level` | Cascade level that should absorb the fix (`exec-summary` … `prd`). |
| `target_artifact` | `doc` (inline edit) \| `notes` (`{level}.notes.yaml`) \| `later` (`later.md`). Park actions set this. |
| `paired_finding_id` | When fix ≠ symptom doc, id of the mirrored stub the orchestrator writes to the partner report. |
| `doc_ref` | Human locator; uses the `.md` filename. |

### `fix_action` enum

`reword` · `refile` · `demote` · `add_constraint` · `park_notes` · `park_later` · `flag_risk` · `scope_change`

`demote` and `scope_change` are **recommendations only** — the skill never applies them without user confirmation and a ledger `r-*` ([decision-ledger.md](decision-ledger.md)).

### Per-lens × per-level allowed `fix_action`

All six devil's-advocate lenses stay active at every level. Constrain **output**, not the question. Values listed are **allowed**; anything not listed is forbidden for that lens at that level.

| Lens | exec-summary | mrd | brd | prd |
|------|--------------|-----|-----|-----|
| **Inversion** | `flag_risk`, `reword`, `refile` | + `add_constraint` | + `park_notes` | + `park_later` |
| **Stakeholder** | `flag_risk`, `reword`, `refile`, `add_constraint` | same | + `park_notes` | + `park_later` |
| **Scale** | `flag_risk`, `reword`, `refile` | + `add_constraint` | + `park_notes` | + `park_later` |
| **Simplicity** | `flag_risk`, `reword`, `refile` — **never** `demote`/`scope_change` | + `park_notes` | + `park_notes` | `refile`, `park_notes`, `park_later`, `flag_risk` |
| **Evidence** | `flag_risk`, `reword`, `refile`, `add_constraint` | same | + `park_notes` | + `park_later` |
| **Dependency** | `flag_risk`, `reword`, `refile`, `add_constraint` | same | + `park_notes` | + `park_later` |

**Global fences (override lens table):**

| Pattern | Rule |
|---------|------|
| Capacity vs timeline (`temporal`, T5-2) | Always `fix_action: flag_risk`; **never** `demote`/`scope_change`. `fix_level: prd` unless a separate `scope_misfiling` finding covers the defect. |
| Anonymous vs personalization (`non_functional`/`stakeholder_gaps`, T7-3) | `add_constraint`/`reword` to state the mode boundary — **never** `demote`. `scope_change` only after explicit human decision. |
| Legal-risk tier (T6-1) | `flag_risk` only — tier surfaces residual risk; human owns the call. |
| `demote`/`scope_change` at ES/MRD/BRD | **Never** — route scope reduction to `flag_risk` + `fix_level: prd` or a human-initiated ledger entry. |

### Specialized finding shapes

#### Legal-risk tier (T6-1) — `assumption_debt` / `economic`

Four-tier, never binary. None auto-block. May trigger [domain-routing.md](domain-routing.md).

```json
{
  "category": "assumption_debt",
  "legal_risk_tier": "yellow",
  "litigation_cost_benefit": "Winning plausible but legal spend exceeds revenue for 3 years",
  "fix_action": "flag_risk",
  "fix_level": "exec-summary"
}
```

| Tier | Meaning |
|------|---------|
| `green` | Regime N/A |
| `yellow` | Compliant position exists, but regime risk stays non-zero (enforcement bias, no-court fines; litigation cost/benefit independent of legal merit) |
| `gray` | Compliance status itself ambiguous — could go either way (distinct from yellow's "have an argument") |
| `red` | Hard procedural gate (license/inspection required) — flagged by cost/time, regardless of public/private |

Evidence preference: real enforcement-in-practice/case statistics over literal statute reading ([expert-panel.md](expert-panel.md)).

#### Buyer-perception risk (T6-1b) — `stakeholder_gaps` / `economic` at MRD

Separate finding, not folded into legal tier. Fires whenever `yellow`/`gray`/`red` is present.

```json
{
  "category": "stakeholder_gaps",
  "doc": "mrd",
  "finding": "Risk-averse buyers avoid offerings with murky compliance posture",
  "paired_legal_finding_id": "bs-012",
  "fix_action": "flag_risk",
  "fix_level": "mrd"
}
```

#### Scope misfiling (T6-3) — `traceability_breaks`

Channel/tech detail defaults to PRD (tactics). Promote to ES **only** when it is itself a hard external constraint — near-monopoly/no practical alternative, or a regulation specifically names that mechanism. Framed as a constraint/dependency, never a URL/vendor dump.

```json
{
  "category": "traceability_breaks",
  "finding": "GDPR consent-capture mechanism described at ES — belongs in tech.md or PRD",
  "fix_action": "refile",
  "fix_level": "prd",
  "target_doc": "prd"
}
```

**Exception:** when near-monopoly or regulation names the mechanism, `fix_action: add_constraint` at ES is valid — not misfiling.

#### Capacity vs timeline (T5-2) — `temporal`

```json
{
  "category": "temporal",
  "finding": "7 Must deliverables vs ~200 hrs — insufficient basis to size",
  "fix_action": "flag_risk",
  "fix_level": "prd",
  "recommendation": "Route to PRD backlog scoring; accepting scope risk is your call"
}
```

#### Requirement explosion (T5-3) — `traceability_breaks`

Judgment trigger — no hardcoded threshold: disproportionate fan-out vs siblings at the same level, or a child set that itself needs another discovery cycle to enumerate. Overflow beyond PRD scope routes to `tech.md`.

```json
{
  "category": "traceability_breaks",
  "finding": "Single PRD feature fans out to 40+ untestable shalls",
  "fix_action": "refile",
  "fix_level": "prd",
  "target_doc": "prd",
  "target_artifact": "doc",
  "recommendation": "Decompose in PRD or park mechanism overflow in tech.md"
}
```

When mechanism-level overflow exceeds PRD's product-facing scope, set `target_artifact: doc` with `target_doc` pointing at overflow destination via recommendation text and route overflow to `tech.md` on address.

## Static vs judgment

[success-criteria.md](success-criteria.md). Judgment only: compound leaves, MoSCoW inflation vs the posture legend, vague AC, missing/wrong posture, off-level facts sitting on the wrong doc.

## Challenge output expectations

**Goal: weak-spot completeness** — surface every relevant weak spot into evidence (a finding). "Discomfort" is the **non-suppression rule**: no weak spot gets skipped for being hard to ask or hard to answer. Discomfort is not the target; completeness is. Invalid output = noise that is not a weak spot (wrong-level, hallucinated, tactics at the wrong doc).

Challenge agent must:

1. Scan **one target doc** per invocation against the **union** of the taxonomy (judgment) — not a per-level `in_scope` slice.
2. Produce at least one finding for that doc (or explicit `no_findings` with justification).
3. Run mandatory self-check before return (challenge agent): `grounding` · `level_fit` · `action_fit` · `non_duplicate` · `distance` · `candor`. Drop or downgrade failures; persist survivors.
4. Respect per-lens × per-level `fix_action` fences (above) and specialized finding shapes.
5. Emit `target_doc` + `paired_finding_id` when fix ≠ symptom doc; orchestrator mirrors the stub into the partner report.
6. Include comparison table when the doc recommends a single approach without alternatives.
7. Never modify docs — findings only; user re-runs `--discover` to apply fixes.
8. Do not re-check parent pointers, ID density, or spec gates when the validator ran.
9. Categories naming a specific domain topic (GDPR, i18n, distribution, …) **may trigger** [domain-routing.md](domain-routing.md) — judgment, once per distinct topic.
