# goal-anchor

**Owner:** Disambiguate vague input, clarify-before-assume, nuance capture, goal re-anchoring, and decision/assumption log format.

**Load when:** Ambiguity, conflict, or nuance detected during inline discovery.

## Disambiguation protocol

When input is vague (multiple valid interpretations):

1. **Name the ambiguity** — State what is unclear in one sentence.
2. **Offer 2–4 concrete options** (not open-ended unless necessary).
3. **Deliver per `question_mode`:**
   - `ask` (default) → `AskQuestion` with options
   - `text` → numbered options inline in chat; user replies in conversation
4. **Capture nuance** — If user picks "other" or adds qualifiers, record full text, not just the label.
5. **Re-anchor** — After resolution, restate the decision tied to the user's stated goal.

Do not proceed to compose until blocking ambiguities are resolved.

## Clarify-before-assume

| Situation | Action |
|-----------|--------|
| Missing fact, non-blocking | Record as `assumption` with `blocking: false`; note in doc |
| Missing fact, blocking | Surface question; do not invent |
| Implied fact from context | Confirm with user before recording |
| Industry default | State the default; ask accept/reject/modify |
| Prior level fact seems wrong | Flag conflict; ask user to reconcile |

**Never silently drop** user qualifiers (e.g. "mostly", "except for", "only in prod").

## Nuance capture

Preserve in `decisions[]` or `level_facts`:

- Scope boundaries ("only enterprise tier", "not mobile")
- Temporal qualifiers ("by Q3", "after migration")
- Conditional behavior ("if SSO enabled")
- Priority signals ("must-have" vs "nice-to-have")
- Negative requirements ("must NOT store PII")

Flattening nuance into generic statements is a gate failure.

## Goal re-anchoring

At each level transition and after major decisions:

1. Restate the user's **primary goal** (from exec-summary vision/problem).
2. Show how the current level's work serves that goal in one sentence.
3. If current facts drift from goal → surface misalignment via question.

## Conflict resolution

When child level contradicts parent:

1. Present both statements side by side.
2. Ask which takes precedence or how to reconcile.
3. Record resolution as `decision` with `type: conflict_resolution`.
4. Update affected `level_facts` in both levels if needed.

## Decision log format

```json
{
  "id": "d-001",
  "level": "prd",
  "type": "decision|assumption|conflict_resolution|nuance",
  "text": "Full decision text with qualifiers preserved",
  "goal_ref": "exec-summary vision statement or objective id",
  "traces_to": "brd-obj-2",
  "blocking": false,
  "user_confirmed": true,
  "timestamp": "ISO-8601"
}
```

## Assumption format

```json
{
  "id": "a-001",
  "level": "mrd",
  "text": "Target market is mid-market SaaS (50-500 employees)",
  "goal_ref": "exec-summary problem statement",
  "blocking": false,
  "source": "user_stated|inferred|search_result",
  "validated": false
}
```

## Question patterns

| Pattern | `ask` mode | `text` mode |
|---------|------------|-------------|
| Single-select | `AskQuestion` single-select | Numbered list; "reply with number" |
| Multi-select | `AskQuestion` multi-select | Bulleted options; "reply with numbers or names" |
| Confirm | `AskQuestion` confirm | "Confirm: [statement] — yes/no?" |
| Free-text follow-up | `AskQuestion` with Other | "Or describe in your own words:" |

After each answer, append to decision log before continuing discovery.

## Session completion signals

Treat as level/session done when user says (case-insensitive intent):

- "done", "that's enough", "good to proceed", "move on", "next level"
- "stop", "pause", "done for now" → checkpoint and exit (not level complete)

Do not advance a level while blocking clarifications remain unless user explicitly accepts gaps.
