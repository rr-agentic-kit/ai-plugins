# proactivity

**Owner:** Active dual-lens loop during Plan — auto-reflection, Effort-without-architecture block, Coach/Fast nudge, write-time pre-save.

**Load when:** Reflect/explore trigger fires during Plan interview (not post-composition research — see [research-method.md](research-method.md)). **Also** at write-time pre-save (after stage-exit + Gate 7 + success-criteria; files on disk). Pre-save does not replace stage-exit or Gate 7.

Panel seats / verdict ladder: [expert-panel.md](expert-panel.md). Sweep/ledger: `refs/planning/decision-ledger.md`. Interview: [plan-interview.md](plan-interview.md).

## Active panel loop (Plan)

After each Plan sub-section:

1. **Mirror back** — 2–3 sentences of what was captured (product **and** system lens).
2. **Sit dual-lens** — Founder product + architecture judgment in one sitting — no role handoff.
3. **Falsify / evidence / alternatives** — expert-panel evidence loop when seats would block.
4. **Probe gaps** — One targeted question:
   - "What happens if [assumption] is wrong?"
   - "Who loses if we succeed?"
   - "What are we explicitly NOT doing?"
   - "Where does this live in the spine vs a feature delta?"
5. **Surface risks** — One risk/tradeoff; classify per expert-panel.
6. **Record** — assumptions/decisions; mint ledger rationale; sweep.

**Hard block:** feature RICE Effort or slice freeze without architecture decision for that capability this pass ([system-design.md](system-design.md)).

**Stop** per expert-panel evidence-loop stop. Cap at one pass per section after that.

## Challenge prompts (Plan-time)

Lightweight devil's-advocate during Plan — not the full `--challenge` agent:

| Trigger | Prompt pattern |
|---------|----------------|
| Single-stakeholder framing | "Who else is affected but not mentioned?" |
| Solution-before-problem | "Restate the outcome without the mechanism." |
| PRD shape confirmed | Run PRD-shape + arch_doc_mode once ([project-posture.md](project-posture.md)). |
| Effort without architecture | **Block** — force spine/delta before Effort. |
| Happy-path only | "What is the primary failure mode?" |
| Sprint / capacity language | Refuse; reframe as slice selection. |
| Coach/Fast not offered this session | Offer once ([plan-interview.md](plan-interview.md)). |
| Seat blocks | Conduct protocol (expert-panel). |
| About to suggest freeze after smell-clean | **Block suggest** until standard challenge clear or risk-accept — "Does this still move [goal_ref] likelihood? Standard challenge clear? Any standing red flag / Discover-reopen open?" ([goal-anchor.md](goal-anchor.md), [execute-handoff.md](execute-handoff.md), `refs/planning/challenge-layers.md`) |
| Auto-reflection at phase transition | Run standing self-challenge ([goal-anchor.md](goal-anchor.md)); never skip because checklist advanced |

## Exploration rules

| Allowed during Plan | Deferred |
|---------------------|----------|
| Frozen business-case facts | Market/GTM re-debate → `rr-discovery` |
| Targeted search for NFR/standards cited in AC | Broad competitor landscape (research phase) |
| Architecture judgment for Effort | Inventing Execute/test code |

## Reflect/explore triggers

Fire reflection when any of:

- User provides >3 paragraphs without structure → offer to extract structured facts.
- Conflicting statements within Plan.
- Gate 5 (proactivity) not yet satisfied.
- User says "I think", "probably", "maybe" on a blocking fact.
- Compose returns `clarifications_needed[]` with `severity: high`.
- PRD shape / arch mode just confirmed.
- Effort requested without spine/delta.
- Sweep enqueued an item, or a seat issued `hold` / `pivot` / `kill`.

## Pre-save reflection (write-time)

Runs **after** stage-exit (Gate 6), Gate 7, and `refs/planning/success-criteria.md`, **after compose files exist**, **before** `session-state.json` persist. Pause / stop does **not** trigger this.

**Block** when ledger open-queue / binding `hold`/`kill` fires. Advisory `hold` at PRD does not block if user accepted it.

1. Run the sweep (trigger 4).
2. **One pass** over remaining gaps (missing non-goal, smell-fail AC without hold, Effort-without-architecture, compose `sections_incomplete`, open queue, **standing red flag / Discover-reopen candidate open**, **auto-reflection not run this transition**).
3. Surface at most a handful of questions; user may accept **non-viability** gaps.
4. **Max one fix cycle** — re-compose once if user supplies fixes.
5. Then skill writes `session-state.json` only.

Do not invent Plan AC into `tech.md`. Do not spawn the challenge agent at pre-save.

## Output to session state

```json
{
  "reflections": [{
    "level": "prd",
    "summary": "",
    "gaps_probed": [],
    "risks_surfaced": [],
    "evidence_bar_met": true,
    "user_confirmed": true
  }],
  "research_deferred": [{
    "topic": "",
    "reason": "requires broad study beyond Plan budget",
    "level": "prd",
    "evidence_bar": ""
  }]
}
```

`user_confirmed` is the user's answer to the pass, not the stop rule. `evidence_bar_met` (or a recorded `hold`) is.
