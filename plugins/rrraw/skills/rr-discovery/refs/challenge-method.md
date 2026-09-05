# challenge-method

**Owner:** Discovery devil's-advocate method — pre-mortem plus strategy red-team — for the challenge agent and deep-chain challenge pass.

**Load when:** `--challenge` / `--review` on discovery stems (`executive-summary`, `mrd`, `brd`), or `depth: deep` appends challenge after cascade compose. The **discovery challenge agent loads this ref**. Plan/PRD challenge keeps its own allowlist; do not apply PRD failure-mode lenses here unless the target doc is in scope.

**Complements:** Blind-spot taxonomy in [blind-spots.md](blind-spots.md) (category scan). This ref owns **how** to attack strategy and kill criteria — not the full taxonomy table.

**Does not:** auto-unfreeze, mint versions, invent TAM, or rewrite cascade docs without skill compose. Findings persist as `{stem}.challenge.report.md`; skill stamps `status.yaml` challenge attestation (`refs/planning/baselines.md`).

## Pre-mortem

Assume the venture / initiative **failed** 12–24 months out. Work backward:

1. List failure narratives (specific, causal — not "execution risk").
2. Classify each failure mode (below).
3. Rank by **impact × likelihood × cheapness-to-test**.
4. Attach evidence bars / timeboxes that would have caught it.

### Tigers / Paper-Tigers / Elephants

| Class | Meaning | Disposition |
|-------|---------|-------------|
| **Tigers** | Real, dangerous, under-attended | Must mitigate, experiment, or change verdict |
| **Paper-Tigers** | Feels scary; weak evidence or cheaply falsifiable | Test cheaply or demote; do not let them dominate |
| **Elephants** | Obvious risks everyone avoids naming | Surface explicitly; force AskQuestion or ledger decision |

Every Tiger needs a named owner disposition: experiment, constraint, non-goal, pivot, or kill-criteria link. Paper-Tigers without a cheap test stay demoted — do not inflate into Gate 7.

## Strategy red-team

**Steelman, then attack.**

1. **Steelman** the current strategy in one short paragraph (fair best case — no strawman).
2. **Attack** along: segment choice, switching trigger, cost position, defensibility (Can't/Won't), GTM reachability, premises, metric teeth.
3. **Rank** attacks by impact × likelihood × cheapness-to-test (same scoring as pre-mortem).
4. Prefer attacks that flip `viability_verdict` or a Must objective — not editorial nitpicks.

Seat pressure may reuse expert-panel personas ([expert-panel.md](expert-panel.md)); challenge agent does not re-run full Gate 7 unless findings are premise-critical — then escalate to skill for re-sit.

## Timebox / kill criteria

For the top Tigers and top red-team attacks, require:

| Field | Rule |
|-------|------|
| **Evidence** | What observation would change our mind |
| **By when** | Date or milestone — not "someday" |
| **Flip** | Which verdict moves (`proceed` → `hold` / `pivot` / `kill`) |

If kill criteria cannot be stated → finding severity at least `high`; skill must park as `open_holds` or force AskQuestion before treating challenge as clean.

Align with L1 timebox language when present. Do not invent dates; `hold` on the timebox is allowed if explicit.

## Ranking formula (ordinal)

Score each finding 1–5 on impact, likelihood, cheapness-to-test (5 = cheapest). Prefer high impact × high likelihood × high cheapness for immediate experiments. Expensive tests on low-likelihood Paper-Tigers → defer.

## Report shape

Orchestrator persists `{stem}.challenge.report.md` with frontmatter `depth`. Body must include:

1. Steelman paragraph
2. Pre-mortem table (Tiger / Paper-Tiger / Elephant + rank + disposition)
3. Red-team attacks ranked
4. Kill criteria / timeboxes
5. Mapping to blind-spot category ids when applicable
6. Residual accepts (user-accepted) vs open

Do not claim `clean-shallow` / `clean-deep` in the report body — skill stamps attestation only when findings are zero for that stem (`refs/planning/baselines.md`).

## Interaction with cascade

| Finding class | Skill action |
|---------------|--------------|
| Premise-critical | Escalate Gate 7 / re-decision queue |
| Doc gap | Re-compose affected level after user confirm |
| Metric decorative / missing kill criteria | Block discovery_complete until fixed or `open_holds` |
| PRD-shaped detail | Park to notes / Plan — out of discovery challenge scope |

## Done-when

- This ref loaded by challenge agent for discovery targets
- Steelman present; classifications complete
- Top risks ranked; kill criteria stated or explicit `hold`
- Report path returned to skill for persist + attestation stamp

## Further reading

Techniques adapted from phuryn/pm-skills (MIT): pre-mortem Tigers/Paper-Tigers/Elephants, strategy red-team steelman-then-attack, cheapest-test ranking.
