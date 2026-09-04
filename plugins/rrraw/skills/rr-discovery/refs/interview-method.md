# interview-method

**Owner:** On-demand customer interview synthesis using Mom Test discipline and JTBD extraction — not a mandatory cascade level.

**Load when:** User provides transcripts / interview notes, or skill/proactivity asks for primary evidence on a blocking Value/Usability assumption. Skip when no interviews exist — do not invent quotes.

**Does not:** replace Gate 7, fabricate personas as freeze requirements, or mint PRD stories. Full persona journeys stay optional research — ICP + segments suffice for freeze ([gtm-framing.md](gtm-framing.md)).

## When to run

| Trigger | Action |
|---------|--------|
| Transcripts or notes available | Synthesize → `interview-synthesis.md` |
| HI×HR Value assumption lacks primary evidence | Offer interview or cheaper pretotype ([ideation.md](ideation.md)); do not block forever on interviews |
| User asks for Mom Test / JTBD pass | Run method on supplied material |
| No source material | Ask for notes or mark evidence `hold` — never hallucinate interviewees |

## Mom Test discipline

Interview for **past behavior and specifics**, not compliments or hypotheticals.

| Prefer | Reject / reframe |
|--------|------------------|
| "Tell me about the last time…" | "Would you use…?" |
| Concrete workarounds, spend, tools | "Sounds great!" as evidence |
| Who else is involved / who blocks | Feature wishlist as commitment |
| What they tried and why it failed | Your pitch validation ("do you like our idea?") |

Rules:

1. Talk about **their life**, not your solution.
2. Ask about **specifics in the past**, not generic futures.
3. Dig for **commitment signals** (time, money, process change) — compliments are noise.
4. If you talked more than they did, the session is weak evidence — flag confidence `low`.

Record confidence per claim: `high` (repeated across interviews) / `medium` / `low` / `hold`.

## JTBD synthesis

From valid interviews, extract Jobs-to-be-Done signals (outcome-shaped, not feature-shaped):

| Field | Question |
|-------|----------|
| **Job** | What progress were they trying to make? |
| **Situation** | When / where / constraints |
| **Push** | Why status quo hurts now |
| **Pull** | What better looks like |
| **Anxiety / habit** | What keeps them stuck |
| **Success** | How they would know it worked |

Map jobs to opportunities on the OST when `opportunity-tree.md` exists ([ideation.md](ideation.md)). Do not invent jobs to fill the table.

Optional 6-part value proposition (Who/Why/What-before/How/What-after/Alternatives) lives in [strategy-lenses.md](strategy-lenses.md) — wire interview outputs there on demand; do not duplicate a mandatory canvas file.

## Synthesis artifact

Persist **`interview-synthesis.md`** when this method runs:

```markdown
# Interview synthesis

## Sources
- … (count, dates, roles — no PII beyond role unless user supplied)

## Behavioral patterns
- …

## JTBD candidates
| Job | Push | Pull | Confidence | Notes |
|-----|------|------|------------|-------|

## Commitment signals
- …

## Non-evidence (compliments / hypotheticals discarded)
- …

## Implications for premises
- Link to assumption ids (`A-n`) or cascade items when promoted
- Explicit `hold` where N is too small
```

Promote durable premises into L1/MRD items + ledger evidence ids. Keep raw quotes out of `business-case.yaml` — handoff cites `artifact_refs.interview_synthesis` only.

## Anti-patterns

| Failure | Fix |
|---------|-----|
| Treating "I'd buy that" as WTP | Demand ≠ pricing ([ideation.md](ideation.md)) |
| One complimentary interview as validation | Confidence `low`; need pattern or pretotype |
| Writing freeze-required personas | Use ICP behaviors instead ([gtm-framing.md](gtm-framing.md)) |
| Inventing TAM from interview anecdotes | Illegal — size in MRD with dual method or `hold` |

## Done-when

- Synthesis file on disk if interviews were processed
- Each claim has confidence + source pointer
- Compliments segregated from behavioral evidence
- Blocking premises either promoted to ledger/items or parked as `open_holds`

## Further reading

Techniques adapted from phuryn/pm-skills (MIT): interview/JTBD synthesis patterns (Mom Test discipline as commonly practiced in discovery kits).
