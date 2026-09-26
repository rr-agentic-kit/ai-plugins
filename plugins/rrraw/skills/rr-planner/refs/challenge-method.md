# challenge-method

**Owner:** Plan technical challenge — pre-mortem **and** assumption red-team — for constitution, feature deltas, and AC. Attacks hollow Effort and altitude misfile.

**Load when:** `--challenge` / `--review` on Plan targets (`prd`, `constitution`, `architecture`, deltas), stage-exit technical row, or `depth: deep` appends challenge. Challenge agent **must** load this ref for Plan targets (`refs/planning/contracts.md`).

**Layers:** `refs/planning/challenge-layers.md`. Bare `--challenge` = **standard** (relevant load-bearing claims). `--challenge deep` = exhaustive. Auto-reflection / smells are **not** this pass.

**Does not:** Re-litigate market/GTM/pricing. Does not auto-unfreeze. Parent keeps **compact** `parent_summary` only — full report on disk. Does not full-load supporting corpus.

**Scoped load:** Per [context-budget.md](context-budget.md) challenge row (one target + named contradiction candidates). Pre-Task budget detect — hard → `CONTEXT_BUDGET_EXCEEDED`.

**Complements:** [blind-spots.md](blind-spots.md) taxonomy. Discover stems use Discover `challenge-method.md` — do not mix.

**Standing self-challenge:** Continuous auto-reflection lives in [goal-anchor.md](goal-anchor.md) (phase transitions). When that reflex finds a load-bearing Discover-level mismatch, recommend scoped `--challenge` (standard) or Plan→Discover reopen — do not wait for the user to notice and ask. Do **not** call user `--challenge` “the deep pass.”

## Depth modes

| Mode | How selected | Coverage | Attestation when clean |
|------|--------------|----------|------------------------|
| **standard** | `--challenge` / `--review` default; skill pre-freeze suggest | All **relevant** load-bearing claims (constitution, deltas, AC, Effort honesty) | `clean-shallow` (`depth: shallow`) |
| **deep** | Explicit `deep` / `--challenge deep` | Every detail / exhaustive | `clean-deep` (`depth: deep`) |

Soft escalation (optional review Task) only on `deep` or heavy cull — `agents/planning/challenge.md`.

## Dual method (both offered)

### 1. Technical pre-mortem

Assume the **slice / standing design failed** in production. Work backward:

1. Failure narratives (specific, causal — not “execution risk”).
2. Classify Tiger / Paper-Tiger / Elephant.
3. Rank by **impact × likelihood × cheapness-to-test**.
4. Attach cheapest probes.

| Class | Meaning | Disposition |
|-------|---------|-------------|
| **Tigers** | Real, dangerous, under-attended | Mitigate, experiment, or change design |
| **Paper-Tigers** | Scary; weak evidence or cheaply falsifiable | Test cheaply or demote |
| **Elephants** | Obvious risks people avoid naming | Surface; force AskQuestion or ledger decision |

### 2. Assumption red-team

**Steelman, then attack** load-bearing claims in constitution + deltas + AC:

1. Steelman the current technical plan in one short paragraph.
2. Attack: boundaries, data model, failure modes, observability of AC, same-sitting Effort honesty (**Effort drivers** cited? Happy-Path?), cost-relevant UX states, altitude misfile.
3. Rank attacks the same way.
4. Cap **3–5 kill-assumptions** — evidence × by-when × flip.

Standard may stop after relevant load-bearing claims. Deep continues until exhaustive coverage of the target surfaces below.

## Target surfaces

| Target | Look for |
|--------|----------|
| Constitution INDEX | Soft invariants, missing `Prevents`, stack/product dump posing as INDEX, UX baseline as component catalog |
| Tech ADR | Product mechanism misfiled as ADR; silent edit of accepted ADR |
| Feature delta | Restated constitution, silent edit of accepted decision, missing rejections, missing **Effort drivers**, missing cost-relevant states / UX-shape on UI-facing; misuse of `ADR-*` ids |
| WWAS AC | Vague verbs, loopholes, unobservable acceptance ([req-smell.md](req-smell.md)); AC written as test code |
| Selection / Effort | Slice that deleted deferred requirements; Effort without standing record; **Happy-Path Effort**; Fibonacci filled after product talk only; **freeze-readiness theater** |
| Altitude misfile | Mechanism parked in PRD; AC as tests; Plan inventing pixels; Execute expected to pick wizard vs form or new integration boundary |
| Grant / access axes | **Axis conflation** — invite / register-tenant / session login / IdP SSO / mailbox OAuth collapsed into one access model ([domain-routing.md](domain-routing.md)) |
| Nature expectations | **Missed nature expectations** — reflection owed vs what landed ([nature-expectation-packs.md](nature-expectation-packs.md)); not “table row unchecked.” Elicit gaps or kill-assumption |
| Context budget | Fat always-load files; research/challenge corpus dumps ignoring scoped load ([context-budget.md](context-budget.md)) |

## Parent summary contract

Challenge agent returns full findings + report body for skill persist. Parent retains only:

- `parent_summary.verdict`
- top finding ids
- `kill_assumptions[]` (≤5)

Do not paste the full report into the fused sitting chat.

## Report shape

`{stem}.challenge.report.md` body includes: steelman, pre-mortem table, red-team ranks, kill-assumptions, blind-spot category mapping, residual accepts vs open. Frontmatter `depth` matches mode map above.

## Done-when

- Both methods available; at least one run unless user explicitly scopes to one
- Mode honored (standard vs deep); attestation stamp matches
- Happy-Path Effort, missing cost-relevant states, and altitude misfile checked when applicable
- Grant/access-axis conflation and missed nature expectations (reflection owed vs landed) probed when nature surfaces apply
- ≤5 kill-assumptions with cheapest probes
- `parent_summary` compact; full report on disk
