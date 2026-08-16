# proactivity

**Owner:** Active panel loop during discovery — auto-reflection, search-vs-research split, reflect triggers, and write-time pre-save.

**Load when:** Reflect/explore trigger fires during inline discovery (not during the post-composition research phase — see [research-method.md](research-method.md)). **Also** at write-time pre-save reflection (after stage-exit blind-spots + Gate 7 + success-criteria; all depths; files already on disk). Pre-save does not replace stage-exit blind-spots or Gate 7.

Panel seats, verdict ladder, claim classes, evidence loop, and owe-an-alternative: [expert-panel.md](expert-panel.md). Sweep and ledger writes: [decision-ledger.md](decision-ledger.md). Pre-save block: that ledger's open-queue / binding `hold`/`kill` rule.

## Active panel loop

After each discovery sub-section (not necessarily each full level):

1. **Mirror back** — Summarize what was captured in 2–3 sentences.
2. **Sit the level's roster** — Name the seats ([expert-panel.md](expert-panel.md)). Domain practitioner is instantiated from `domain_context`.
3. **Falsify / evidence / alternatives** — Run [expert-panel.md](expert-panel.md) evidence loop and, if a seat would block, that ref's conduct protocol.
4. **Probe gaps** — One targeted question the user has not addressed:
   - "What happens if [assumption] is wrong?"
   - "Who loses if we succeed?"
   - "What are we explicitly NOT doing?"
5. **Surface risks** — Name one risk or tradeoff implied by current facts. Classify per [expert-panel.md](expert-panel.md).
6. **Record** — Add surfaced items to `assumptions[]` or `decisions[]` in session state. Mint a ledger rationale when the decision is made. Write evidence records from any search this pass. Run the sweep.

**Stop** per [expert-panel.md](expert-panel.md) evidence-loop stop. Cap at one pass per level section after that (avoid interrogation fatigue).

## Challenge prompts (discovery-time)

Lightweight devil's-advocate during discovery — not the full `--challenge` agent:

| Trigger | Prompt pattern |
|---------|----------------|
| Single-stakeholder framing | "Who else is affected but not mentioned?" |
| Solution-before-problem | "Restate the problem without mentioning the solution." |
| PRD MoSCoW assigned | Run the **cut-pass** once ([project-posture.md](project-posture.md)). Do not ask a generic "v1 or future phase?" |
| Happy-path only | "What is the primary failure mode?" |
| Market / economic claim without evidence | Classify and run the evidence loop ([expert-panel.md](expert-panel.md)). Do not defer TAM/SAM/SOM to research when `premise-critical`. |
| Seat blocks | Conduct protocol ([expert-panel.md](expert-panel.md)). |

## Exploration rules

| Allowed during discovery | Deferred to research phase |
|--------------------------|---------------------------|
| User's stated competitors | Broad competitor landscape scan |
| User's known regulations | Standards/regulatory deep dive |
| Premise-critical sizing and "what must be true" (external TAM/SAM/SOM **or** internal cost-of-inaction) | Multi-round citation-backed evaluation beyond the class budget |
| "I think X because Y" validation | Exhaustive adjacent-market study |
| Targeted search within the **claim-class budget** | Research iterations after compose |

Search budgets and evidence loop: [expert-panel.md](expert-panel.md). Search to validate a specific claim or fill a blocking gap — not to decorate. Residual gap broader than the class budget → that ref's evidence-loop stop (`hold` or `research_deferred[]`).

## Reflect/explore triggers

Fire reflection when any of:

- User provides >3 paragraphs without structure → offer to extract structured facts.
- Conflicting statements detected within same level.
- Level gate 5 (proactivity) not yet satisfied.
- User says "I think", "probably", "maybe" on a blocking or `premise-critical` fact.
- Compose agent returns `clarifications_needed[]` with `severity: high`.
- PRD MoSCoW just assigned → cut-pass (once per PRD compose; same fatigue cap as Gate 5).
- Sweep enqueued an item, or a seat issued `hold` / `pivot` / `kill`.
- Evidence round just landed (always sweep; reflect if anything invalidated).

## Pre-save reflection (write-time)

Runs **after** stage-exit blind-spots (Gate 6), Gate 7 viability, and [success-criteria.md](success-criteria.md), **after compose files exist**, **before** the skill's `session-state.json` persist. All depths. Pause / stop does **not** trigger this.

**Block** when [decision-ledger.md](decision-ledger.md) open-queue / binding `hold`/`kill` rule fires (do not write `final_status: ok`; do not freeze leftover drafts as accepted). Advisory `hold` at BRD/PRD/FRD does not block if the user accepted it.

This is thinner than discovery-time Gate 5 and does **not** re-run the blind-spot taxonomy:

1. Run the sweep (trigger 4).
2. **One pass** over remaining gaps and obvious improvements (missing non-goal, unmeasurable metric, unaccepted `blocking` assumption, compose `sections_incomplete`, open queue, binding `hold`).
3. Surface at most a handful of questions; user may accept **non-viability** gaps. User may not silently accept an open queue or binding `hold`/`kill` — drain, pivot, or confirm kill with a revival trigger.
4. **Max one fix cycle** — re-compose affected levels once if the user supplies fixes (compose overwrites files). Do not loop.
5. Then skill writes `session-state.json` only.

Do not invent FRD-level detail during pre-save of an earlier level. Do not spawn the challenge agent.

## Output to session state

```json
{
  "reflections": [{
    "level": "brd",
    "summary": "",
    "gaps_probed": [],
    "risks_surfaced": [],
    "evidence_bar_met": true,
    "user_confirmed": true
  }],
  "research_deferred": [{
    "topic": "",
    "reason": "requires broad market study beyond claim-class budget",
    "level": "mrd",
    "evidence_bar": ""
  }]
}
```

`user_confirmed` is the user's answer to the pass, not the stop rule. `evidence_bar_met` (or a recorded `hold`) is.
