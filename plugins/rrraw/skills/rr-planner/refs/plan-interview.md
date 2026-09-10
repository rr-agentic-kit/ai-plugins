# plan-interview

**Owner:** Plan interview flow — objective → capability → story → feature → requirements; Coach vs Fast; same-sitting score+architect.

**Load when:** Plan compose/change after entry gate and posture; every Q&A cycle for Plan.

**Does not:** Re-run Discover ideation/viability. Does not use sprint ceremony. Does not “fill PRD §N” as interview chrome.

## Audience

One founder, **two lenses in one sitting** (product + system) — no human routing between PM and Architect skills.

## Modes (offer once per Plan session start)

| Mode | Behavior |
|------|----------|
| **Coaching** (default) | Elicit; one question/cycle default; notes sidecar before questions; after nature reflection, elicit each **derived** expectation |
| **Fast** | Speed path; mark invented facts with `[ASSUMPTION]` tags. **Stop-rule:** may `[ASSUMPTION]`-tag, but **must not** invent a single merged invite-only (or similar) access model when nature reflection surfaces multiple axes — cover **derived** expectations per-axis or explicit **per-axis** assumptions. Refuse silent conflation. |

Persist preference on `session_state.project_posture.interview_mode` when confirmed (`coach` \| `fast`).

## Flow

```
objective → capability → story → feature → full requirement set (P1–P3)
         ↘ same-sitting: RIC/RICE Effort + architecture (spine and/or delta)
         → select via _status_ → WWAS AC + req-smell → optional challenge → slice freeze
```

1. Anchor on frozen business-case / BRD objectives — do not reopen market.
2. Name capabilities that deliver objectives. After capability naming, load [nature-expectation-packs.md](nature-expectation-packs.md) and **run reflect → elicit**: name nature surfaces → derive which expectation classes apply for this project (and which do not) → Coach asks; Fast still covers derived expectations (answer or per-axis `[ASSUMPTION]`). Do not wait for a founder dump; do not dump a universal checklist.
3. Stories: outcome form default — `As [persona], I can… so that…`. Optional **job story** body for B2B/situation-heavy: `When… I want… so I can…` — not a second backlog.
4. Features: RICE; stories: RIC ([prioritization-lens.md](prioritization-lens.md)).
5. **Hard stop:** [system-design.md](system-design.md) same-sitting rule — Decision + **Effort drivers** (+ UX-shape when UI-facing); [adr-lite.md](adr-lite.md) when ADR shape applies. Refuse Effort without drivers. Access axes stay separate mechanisms ([domain-routing.md](domain-routing.md)).
6. Capture the **full** requirement set; select build-now with `_status_:` — never delete deferred rows.
7. Narrowing interview: talk capability/cost drivers — never “fill PRD §6.”

## Question discipline

- Default one AskQuestion per cycle (`preferences.questions_per_cycle`)
- Notes sidecar before questions for off-level answers ([note-sessions.md](note-sessions.md))
- Anti-triggers: sprint / capacity / velocity → refuse; reframe as slice selection ([input-resolution.md](input-resolution.md))
- **Fast + nature reflection:** when reflection surfaces multiple access axes, refuse a single conflated access model; cover derived expectations or state per-axis assumptions (`invite` ≠ `register-tenant` ≠ `login` ≠ `IdP` ≠ `mailbox OAuth`)

## Done-when

- Coach/Fast offered once this session
- Same-sitting score+architect honored
- Derived-in-scope nature expectations covered (elicited, per-axis assumed, or explicit defer)
- Full requirement set retained; selection is status-only
