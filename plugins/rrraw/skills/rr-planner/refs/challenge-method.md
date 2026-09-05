# challenge-method

**Owner:** Plan technical challenge — pre-mortem **and** assumption red-team — for spine, feature deltas, and AC.

**Load when:** `--challenge` / `--review` on Plan targets (`prd`, `architecture`, deltas), stage-exit technical row, or `depth: deep` appends challenge. Challenge agent **must** load this ref for Plan targets (`refs/planning/contracts.md`).

**Complements:** [blind-spots.md](blind-spots.md) taxonomy. Discover stems use Discover `challenge-method.md` — do not mix.

**Does not:** Re-litigate market/GTM/pricing. Does not auto-unfreeze. Parent keeps **compact** `parent_summary` only — full report on disk.

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

**Steelman, then attack** load-bearing claims in spine + deltas + AC:

1. Steelman the current technical plan in one short paragraph.
2. Attack: boundaries, data model, failure modes, observability of AC, same-sitting Effort honesty.
3. Rank attacks the same way.
4. Cap **3–5 kill-assumptions** — evidence × by-when × flip.

## Target surfaces

| Target | Look for |
|--------|----------|
| Spine | Soft invariants, missing `Prevents`, stack dump posing as spine |
| Feature delta | Restated spine, silent edit of accepted ADR, missing rejections |
| WWAS AC | Vague verbs, loopholes, unobservable acceptance ([req-smell.md](req-smell.md)) |
| Selection | Slice that deleted deferred requirements; Effort without architecture |

## Parent summary contract

Challenge agent returns full findings + report body for skill persist. Parent retains only:

- `parent_summary.verdict`
- top finding ids
- `kill_assumptions[]` (≤5)

Do not paste the full report into the fused sitting chat.

## Report shape

`{stem}.challenge.report.md` body includes: steelman, pre-mortem table, red-team ranks, kill-assumptions, blind-spot category mapping, residual accepts vs open.

## Done-when

- Both methods available; at least one run unless user explicitly scopes to one
- ≤5 kill-assumptions with cheapest probes
- `parent_summary` compact; full report on disk
