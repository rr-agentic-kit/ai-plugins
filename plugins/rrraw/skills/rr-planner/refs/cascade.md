# cascade

**Owner:** Top-down level order, inheritance/narrowing rules, and per-level completion gates.

## Level order

Fixed sequence — never skip a level in `standard`/`deep` depth (shallow depth trims per input-resolution):

```
1. exec-summary  — vision, problem, why
2. mrd           — market context
3. brd           — business requirements
4. prd           — product requirements
5. frd           — functional detail
```

## Inheritance model

Each level **inherits** all resolved facts from levels above and **narrows** scope:

| Level | Inherits from | Narrows to |
|-------|---------------|------------|
| exec-summary | user input, conversation | strategic vision and problem framing |
| mrd | exec-summary | market segments, competitors, trends relevant to vision |
| brd | exec-summary + mrd | business objectives, stakeholders, constraints |
| prd | exec-summary + mrd + brd | product capabilities, user outcomes, priorities |
| frd | all above | functional behaviors, acceptance criteria, interfaces |

### Inheritance rules

1. **No contradiction** — child facts must align with parent facts. Conflict → [goal-anchor.md](goal-anchor.md) + question (per `question_mode`).
2. **No orphan requirements** — every child requirement traces to a parent objective (verified at success-criteria gate).
3. **Explicit narrowing** — when a parent fact is too broad for the child level, record the narrowing as a decision in the session decision log.
4. **Deferred detail** — details not yet known at a level are recorded as `assumptions[]` or `open_questions[]`, not silently invented.

## Per-level discovery flow (skill-inline)

For each level in `cascade_levels`:

1. Load `doc-standards/<level>.md` for the current level.
2. Extract required sections from the standard.
3. Run progressive discovery:
   - Present inherited facts summary to user (brief).
   - Ask targeted questions for gaps in required sections.
   - On vague input → disambiguate per [goal-anchor.md](goal-anchor.md).
   - On reflect trigger → apply [proactivity.md](proactivity.md).
4. Accumulate `level_facts` object for compose agent.
5. Gate check (below).
6. Invoke compose agent.
7. While `clarifications_needed[]` non-empty → surface question → merge answer → re-invoke compose. Loop until cleared or user says done.

## Stop and resume

User may stop at any point ("stop", "pause", "done for now", etc.):

1. Write partial composed docs for completed levels.
2. Checkpoint full `session-state.json` to `--output-dir` (see [output-formats.md](output-formats.md)).
3. Set `checkpoint.status: paused` with `current_level` and `pending_clarifications`.

To resume: `rr-planner --resume --output-dir <same-dir>` (or NL "continue planning"). Skill loads checkpoint and picks up at `current_level`.

## Per-level completion gates

A level is **complete** only when all gates pass:

### Gate 1: Section coverage

Every **required section** in the matching doc-standard has at least one resolved fact or explicit assumption marked `blocking: false`.

### Gate 2: Goal anchor

- Zero unresolved ambiguities at this level.
- All decisions recorded in session decision log with `goal_ref`.
- Nuance captured where user provided qualifiers (not flattened).

### Gate 3: Inheritance integrity

- No contradictions with parent levels.
- Every new requirement at this level has a `traces_to` parent objective.

### Gate 4: Compose acceptance

- Compose agent returns `status: ok` or user accepted `status: partial` with documented gaps.
- Written doc passes doc-standard **done-when** checklist.

### Gate 5: Proactivity (standard/deep depth only)

- At least one reflection pass completed (see [proactivity.md](proactivity.md)).
- Open risks or assumptions surfaced to user before advancing.

## Advancing vs stopping

| Condition | Action |
|-----------|--------|
| All gates pass | Advance to next cascade level |
| Pending clarifications or gate gaps | Surface question → re-discover or re-compose (no round cap) |
| User says done for level | Accept current state; advance or checkpoint per user intent |
| User requests stop / pause | Checkpoint `session-state.json`; write partial docs; exit cleanly |
| `--resume` | Load checkpoint; continue from `current_level` |

## Fact accumulation schema

Skill maintains across levels:

```json
{
  "decisions": [{ "id": "d1", "level": "exec-summary", "text": "", "goal_ref": "", "timestamp": "" }],
  "assumptions": [{ "id": "a1", "level": "mrd", "text": "", "blocking": false, "goal_ref": "" }],
  "level_facts": {
    "exec-summary": {},
    "mrd": {},
    "brd": {},
    "prd": {},
    "frd": {}
  },
  "composed_docs": {
    "exec-summary": "",
    "mrd": "",
    "brd": "",
    "prd": "",
    "frd": ""
  },
  "checkpoint": {
    "status": "in_progress|paused|complete",
    "current_level": "brd",
    "pending_clarifications": [],
    "question_mode": "ask",
    "updated": "ISO-8601"
  }
}
```

Checkpointed to `--output-dir/session-state.json` on stop and after each level completion. Resume loads this file.
