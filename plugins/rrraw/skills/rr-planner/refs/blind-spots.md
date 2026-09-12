# blind-spots

**Plan scope:** Stage-exit scans the **technical-plan** row (PRD + standing architecture / deltas / AC). Discover ES/MRD/BRD challenge uses `rr-discovery` challenge-method + Discover blind-spots. Do not re-run Discover Gate 7 lenses as Plan inventiveness.

**Owner:** Global blind-spot taxonomy, per-level applicability, alternatives analysis, and devil's-advocate patterns.

**Load when:** Stage-exit (skill-inline, **this level's row** only) **and** `--challenge` / `--review` (challenge agent, **union** of all rows). Plan challenge also loads [challenge-method.md](challenge-method.md).

Do not copy this taxonomy into [doc-standards/](doc-standards/). Those files own required sections and done-when. Each standard points at its applicability row.

## Skill-inline vs agent

| Path | Who | Scope | Output |
|------|-----|-------|--------|
| Stage-exit | Skill (inline, not `Task`) | `in_scope` + `inherit_check` for the current Plan surface | Findings merged via re-compose or assumptions; **no** per-level challenge report |
| `--challenge` | Challenge agent | **One target doc** per invocation; **union** taxonomy + Plan challenge-method | Per-doc `{stem}.challenge.report.md`; parent keeps compact `parent_summary` |

Do **not** spawn the challenge agent per level. Alternatives analysis only for major decisions **in scope at that level**.

### Stage-exit rules

- One pass per surface against that row.
- `critical` / `high` → questioning ([goal-anchor.md](goal-anchor.md)) before freeze.
- **Premise-critical** → escalate into **Gate 7**, not a medium assumption.
- `medium` / `low` → assumptions / open questions; do not block unless the user wants them.
- User may explicitly accept remaining findings. User may not silently accept a premise-critical finding — it becomes Gate 7.
- Findings that belong in the doc merge via re-compose.
- Skip static ref/id findings when `validate_planning.sh` already ran.

### Challenge rules

- One target doc per invocation; scan the union taxonomy on that doc only.
- Plan targets: inject Plan [challenge-method.md](challenge-method.md) (pre-mortem **and** red-team).
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
| `economic` | Hidden costs, revenue model gaps, unit economics, cost of inaction, sizing proxies | growth-investor, CFO |
| `temporal` | Sequencing risks, dependency chains, why-now, approval timing, posture, RICE vs posture legend, Must inflation under `signed_v1` | founder/CEO, seed-investor |
| `assumption_debt` | Unvalidated assumptions treated as facts | seed-investor, domain-practitioner |
| `traceability_breaks` | Judgment: compound leaves, inflated MoSCoW, untestable shalls, off-level facts, requirement-explosion → standing delta/spine (not Plan AC into `tech.md`) | head-of-product, staff-engineer |
| `negative_space` | What is explicitly out of scope and why | founder/CEO, head-of-product |

## Applicability matrix

Stage-exit scans **only** `in_scope` + `inherit_check` for the current level. `defer` lenses must not fire at this stage. `--challenge` ignores this restriction and uses the union.

| Level | `in_scope` | `inherit_check` | `defer` |
|-------|------------|-----------------|---------|
| **executive-summary** | `negative_space`; `temporal` (why now **and** posture); `economic` (cost of inaction); `stakeholder_gaps`; `assumption_debt` | — | Competitive detail → MRD. System failure modes / NFR → PRD when product commitment, else Discover `tech.md` parking / later Plan spine |
| **mrd** | `competitive`; `economic`; `stakeholder_gaps`; `temporal`; `assumption_debt` | Exec-summary non-goals still hold | Failure modes / NFR → PRD when product commitment, else parking / Plan spine |
| **brd** | `stakeholder_gaps`; `economic`; `operational`; `temporal`; `assumption_debt` | Do not re-litigate MRD landscape | Failure modes / NFR / product Won't → PRD when product commitment, else parking / Plan spine |
| **prd** (technical-plan stage-exit) | `failure_modes`; `non_functional`; `operational`; `negative_space`; `temporal` (RICE vs posture; Effort-without-architecture; selection shrink); `stakeholder_gaps`; `traceability_breaks` (compound stories; smell-fail AC; requirement-explosion → **feature delta / spine**, not AC→`tech.md`); alternatives on major features | Personas/objectives vs BRD; competitive/economic only for **contradiction** — no new market debate | Mechanism → `architecture.md` / `deltas/`; never author Plan product AC into root `tech.md` |

## Alternatives analysis

For each major decision **in scope**:

1. Name 2–3 alternatives including "do nothing" where applicable.
2. Compare on: effort, risk, time-to-value, reversibility.
3. State recommendation tied to stated goals.
4. Flag single-option docs without justification.

```markdown
| Option | Effort | Risk | Time-to-value | Reversibility | Fit to goal |
|--------|--------|------|---------------|---------------|-------------|
| A: ... | Low | Med | Fast | High | Strong |
```

## Devil's-advocate prompts

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
  "recommendation": "Add rollback acceptance criteria or defer migration",
  "fix_action": "flag_risk",
  "fix_level": "prd",
  "target_artifact": "doc",
  "paired_finding_id": null,
  "alternatives": []
}
```

### `fix_action` enum

`reword` · `refile` · `demote` · `add_constraint` · `park_notes` · `park_later` · `flag_risk` · `scope_change`

`demote` and `scope_change` are recommendations only — user confirms before ledger write.

### Per-lens × per-level allowed `fix_action`

| Lens | executive-summary | mrd | brd | prd |
|------|--------------|-----|-----|-----|
| **Inversion** | `flag_risk`, `reword`, `refile` | + `add_constraint` | + `park_notes` | + `park_later` |
| **Stakeholder** | `flag_risk`, `reword`, `refile`, `add_constraint` | same | + `park_notes` | + `park_later` |
| **Scale** | `flag_risk`, `reword`, `refile` | + `add_constraint` | + `park_notes` | + `park_later` |
| **Simplicity** | `flag_risk`, `reword`, `refile` — never `demote`/`scope_change` | + `park_notes` | + `park_notes` | `refile`, `park_notes`, `park_later`, `flag_risk` |
| **Evidence** | `flag_risk`, `reword`, `refile`, `add_constraint` | same | + `park_notes` | + `park_later` |
| **Dependency** | `flag_risk`, `reword`, `refile`, `add_constraint` | same | + `park_notes` | + `park_later` |

**Global fences:**

| Pattern | Rule |
|---------|------|
| Capacity / sprint framing (`temporal`) | Always `flag_risk`; never `demote`/`scope_change`. Reframe as slice selection. |
| Anonymous vs personalization | `add_constraint`/`reword` — never `demote`. |
| Legal-risk tier (T6-1) | `flag_risk` only. |
| `demote`/`scope_change` at ES/MRD/BRD | Never — route to `flag_risk` + `fix_level: prd`. |
| Plan AC → `tech.md` | Never — refile to PRD WWAS / feature delta / spine. |

### Specialized shapes

**Legal-risk tier (T6-1):** `green` \| `yellow` \| `gray` \| `red` — never auto-block; may trigger [domain-routing.md](domain-routing.md).

**Buyer-perception (T6-1b):** Separate MRD finding when yellow/gray/red present.

**Scope misfiling:** Mechanism at wrong altitude → refile to Plan delta/spine or PRD outcome — not Plan AC into `tech.md`.

**Requirement explosion:** Decompose; mechanism in `deltas/<feature-id>.md`.

## Static vs judgment

`refs/planning/success-criteria.md`. Judgment: compound leaves, MoSCoW inflation, vague AC, Effort-without-architecture, AC→`tech.md`.

## Challenge output expectations

Weak-spot completeness. Challenge agent must:

1. Scan one target doc against the taxonomy union.
2. For Plan targets, apply [challenge-method.md](challenge-method.md) and return compact `parent_summary`.
3. Produce ≥1 finding or explicit `no_findings`.
4. Self-check: `grounding` · `level_fit` · `action_fit` · `non_duplicate` · `distance` · `candor`.
5. Respect `fix_action` fences; emit dual-stub fields when needed.
6. Never modify docs; do not re-check static graph when validator ran.
7. Domain topics may trigger [domain-routing.md](domain-routing.md).
