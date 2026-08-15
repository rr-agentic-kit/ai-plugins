# proactivity

**Owner:** Auto-reflection loop, challenge prompts, exploration, and targeted-search rules during discovery.

**Load when:** Reflect/explore trigger fires during inline discovery (not during research phase — see [research-method.md](research-method.md)). **Also** at write-time pre-save reflection (after stage-exit blind-spots + success-criteria; all depths). Pre-save does not replace stage-exit blind-spots.

## Auto-reflection loop

After each discovery sub-section (not necessarily each full level):

1. **Mirror back** — Summarize what was captured in 2–3 sentences.
2. **Probe gaps** — Ask one targeted question the user has not addressed:
   - "What happens if [assumption] is wrong?"
   - "Who loses if we succeed?"
   - "What are we explicitly NOT doing?"
3. **Surface risks** — Name one risk or tradeoff implied by current facts.
4. **Record** — Add surfaced items to `assumptions[]` or `decisions[]` in session state.

Stop reflection loop when user confirms "accurate" or after one pass per level section (avoid interrogation fatigue).

## Challenge prompts (discovery-time)

Lightweight devil's-advocate during discovery — not the full `--challenge` agent:

| Trigger | Prompt pattern |
|---------|----------------|
| Single-stakeholder framing | "Who else is affected but not mentioned?" |
| Solution-before-problem | "Restate the problem without mentioning the solution." |
| Scope creep signal | "Is [feature X] essential for v1 or a future phase?" |
| Happy-path only | "What is the primary failure mode?" |
| Market claim without evidence | "What evidence supports [claim]? (defer to research if unknown)" |

## Exploration rules

| Allowed during discovery | Deferred to research phase |
|--------------------------|---------------------------|
| User's stated competitors | Broad competitor landscape scan |
| User's known regulations | Standards/regulatory deep dive |
| Quick fact-check of one claim | Market sizing / TAM-SAM-SOM |
| "I think X because Y" validation | Citation-backed market evaluation |
| Targeted search: 1–2 queries max | Multi-round research with citations |

### Targeted search constraints

- Max **2 lightweight searches** per cascade level during discovery.
- Search only to validate a specific user claim or fill a blocking gap.
- Record search result as assumption with `source` field; do not treat as verified fact without user confirmation.
- If gap requires broad study → add to `research_deferred[]` for post-composition research phase.

## Reflect/explore triggers

Fire reflection when any of:

- User provides >3 paragraphs without structure → offer to extract structured facts.
- Conflicting statements detected within same level.
- Level gate 5 (proactivity) not yet satisfied.
- User says "I think", "probably", "maybe" on a blocking fact.
- Compose agent returns `clarifications_needed[]` with `severity: high`.

## Pre-save reflection (write-time)

Runs **after** stage-exit blind-spots (Gate 6) and [success-criteria.md](success-criteria.md), **before** writing human docs. All depths. Pause / stop does **not** trigger this.

This is thinner than discovery-time Gate 5 and does **not** re-run the blind-spot taxonomy:

1. **One pass** over remaining gaps and obvious improvements (missing non-goal, unmeasurable metric, unaccepted `blocking` assumption, compose `sections_incomplete`).
2. Surface at most a handful of questions; user may accept gaps.
3. **Max one fix cycle** — re-compose affected levels once if the user supplies fixes. Do not loop.
4. Then write md|yaml docs + `items.json` + `session-state.json`.

Do not invent FRD-level detail during pre-save of an earlier level. Do not spawn the challenge agent.

## Output to session state

```json
{
  "reflections": [{
    "level": "brd",
    "summary": "",
    "gaps_probed": [],
    "risks_surfaced": [],
    "user_confirmed": true
  }],
  "research_deferred": [{
    "topic": "",
    "reason": "requires broad market study",
    "level": "mrd"
  }]
}
```
