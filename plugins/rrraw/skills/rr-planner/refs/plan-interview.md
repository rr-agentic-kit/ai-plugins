# plan-interview

**Owner:** Plan interview flow — objective → capability → story → feature → requirements; Coach vs Fast; same-sitting score+architect.

**Load when:** Plan compose/change after entry gate and posture; every Q&A cycle for Plan.

**Does not:** Re-run Discover ideation/viability. Does not use sprint ceremony. Does not “fill PRD §N” as UX.

## Audience

One founder, **two lenses in one sitting** (product + system) — no human routing between PM and Architect skills.

## Modes (offer once per Plan session start)

| Mode | Behavior |
|------|----------|
| **Coaching** (default) | Elicit; one question/cycle default; notes sidecar before questions |
| **Fast** | Speed path; mark invented facts with `[ASSUMPTION]` tags |

Persist preference on `session_state.project_posture.interview_mode` when confirmed (`coach` \| `fast`).

## Flow

```
objective → capability → story → feature → full requirement set (P1–P3)
         ↘ same-sitting: RIC/RICE Effort + architecture (spine and/or delta)
         → select via _status_ → WWAS AC + req-smell → optional challenge → slice freeze
```

1. Anchor on frozen business-case / BRD objectives — do not reopen market.
2. Name capabilities that deliver objectives.
3. Stories: outcome form default — `As [persona], I can… so that…`. Optional **job story** body for B2B/situation-heavy: `When… I want… so I can…` — not a second backlog.
4. Features: RICE; stories: RIC ([prioritization-lens.md](prioritization-lens.md)).
5. **Hard stop:** no feature Effort and no slice freeze until architecture for that capability exists this pass ([system-design.md](system-design.md), [adr-lite.md](adr-lite.md)).
6. Capture the **full** requirement set; select build-now with `_status_:` — never delete deferred rows.
7. Narrowing UX: talk capability/cost — never “fill PRD §6.”

## Question discipline

- Default one AskQuestion per cycle (`preferences.questions_per_cycle`)
- Notes sidecar before questions for off-level answers ([note-sessions.md](note-sessions.md))
- Anti-triggers: sprint / capacity / velocity → refuse; reframe as slice selection ([input-resolution.md](input-resolution.md))

## Done-when

- Coach/Fast offered once this session
- Same-sitting score+architect honored
- Full requirement set retained; selection is status-only
