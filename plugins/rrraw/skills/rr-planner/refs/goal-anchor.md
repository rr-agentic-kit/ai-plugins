# goal-anchor

**Owner:** Disambiguate vague input, clarify-before-assume, nuance capture, goal re-anchoring, and decision/assumption log format.

**Load when:** Entire discovery pass at every cascade level (always-on). Not a trigger. Also on parent/child fact conflict, posture confirm, and off-level owner ambiguity.

Unclear and ambiguous user statements are **blocking**. Do not record them as facts, and do not treat an unresolved guess as a true assumption, until the protocol below completes or the user explicitly accepts an `assumption` with `blocking` set.

## Unclear vs ambiguous

| Kind | Test | Action |
|------|------|--------|
| **Unclear** | Cannot parse a single meaning | Ask; do not guess. Do not record as fact. |
| **Ambiguous** | Two or more valid meanings | Name the ambiguity, offer 2–4 options, capture nuance. Do not pick silently. |

Both block advancing the level unless the user explicitly accepts the gap.

## Disambiguation protocol

When input is unclear or ambiguous:

1. **Name the ambiguity** — State what is unclear in one sentence.
2. **Offer 2–4 concrete options** (not open-ended unless necessary).
3. **Deliver per `question_mode`:**
   - `ask` (default) → `AskQuestion` with options
   - `text` → numbered options inline in chat; user replies in conversation
4. **Capture nuance** — If user picks "other" or adds qualifiers, record full text, not just the label.
5. **Re-anchor** — After resolution, restate the decision tied to the user's stated goal.
6. **Append history** — After every Q&A turn, append to `raw-history/{UTC}.yaml` ([output-formats.md](output-formats.md)).

Do not proceed to compose (and do not freeze the level) until blocking clarifications are resolved or explicitly accepted.

Parent-id existence, numbering, spec/build legality, and md|yaml vs `items.json` drift are **static** — `scripts/validate_planning.py`. This ref owns judgment only (vague input, conflict, nuance). Do not re-check whether a parent id exists.

## Clarify-before-assume

| Situation | Action |
|-----------|--------|
| Missing fact, non-blocking | Record as `assumption` with `blocking: false`; note in doc |
| Missing fact, blocking | Surface question; do not invent |
| Unclear statement | Ask; do not guess; do not record as fact |
| Ambiguous statement | Name it; offer options; do not record as fact until resolved |
| Implied fact from context | Confirm with user before recording |
| Inferred `existence` / `commitment` from repo scan | Confirm before recording `project_posture` ([project-posture.md](project-posture.md)) |
| Off-level owner unclear | Ask which document owns this answer ([note-sessions.md](note-sessions.md)); do not record on the current level |
| Industry default | State the default; ask accept/reject/modify |
| Prior level fact seems wrong | Flag conflict; ask user to reconcile |
| User accepts a gap | Record as `assumption` with `blocking` set as the user stated; not as fact |

**Never silently drop** user qualifiers (e.g. "mostly", "except for", "only in prod").

**Never record as fact** a statement that is still unclear or ambiguous. An accepted gap is an assumption, not truth.

## Nuance capture

Preserve in `decisions[]` or `level_facts`:

- Scope boundaries ("only enterprise tier", "not mobile")
- Temporal qualifiers ("by Q3", "after migration")
- Conditional behavior ("if SSO enabled")
- Priority signals (MoSCoW / Kano / triad class — never P0/P1/P2)
- Negative requirements ("must NOT store PII")

Flattening nuance into generic statements is a gate failure.

## Goal re-anchoring

At each level transition and after major decisions:

1. Restate the user's **primary goal** (from exec-summary vision/problem — `ES-*` ids).
2. Show how the current level's work serves that goal in one sentence.
3. If current facts drift from goal → surface misalignment via question.

## Conflict resolution

When child level contradicts parent:

1. Present both statements side by side.
2. Ask which takes precedence or how to reconcile.
3. Record resolution as `decision` with `type: conflict_resolution`.
4. Update affected `level_facts` in both levels if needed.

## Decision log format

Stored in `session-state.json` (not raw-history). Verbatim Q&A is YAML history only.

```json
{
  "id": "d-001",
  "level": "prd",
  "type": "decision|assumption|conflict_resolution|nuance|project_posture|scope_change|note_routed",
  "text": "Full decision text with qualifiers preserved",
  "goal_ref": "ES-1",
  "parent": "BRD-2",
  "blocking": false,
  "user_confirmed": true,
  "timestamp": "ISO-8601"
}
```

| `type` | When |
|--------|------|
| `project_posture` | Existence × commitment confirmed |
| `scope_change` | New Must after `signed_v1` (or reject inflation) |
| `note_routed` | Off-level answer parked, deepened, applied, or discarded |

## Assumption format

```json
{
  "id": "a-001",
  "level": "mrd",
  "text": "Target market is mid-market SaaS (50-500 employees)",
  "goal_ref": "ES-2",
  "blocking": false,
  "source": "user_stated|inferred|search_result",
  "validated": false
}
```

`source: inferred` requires confirm-before-record. Do not set `validated: true` unless the user confirmed or evidence landed.

## Question patterns

| Pattern | `ask` mode | `text` mode |
|---------|------------|-------------|
| Single-select | `AskQuestion` single-select | Numbered list; "reply with number" |
| Multi-select | `AskQuestion` multi-select | Bulleted options; "reply with numbers or names" |
| Confirm | `AskQuestion` confirm | "Confirm: [statement] — yes/no?" |
| Free-text follow-up | `AskQuestion` with Other | "Or describe in your own words:" |

After each answer: append raw-history YAML, then update the decision/assumption log in session state, then continue discovery. Off-level answers: classify owner first ([note-sessions.md](note-sessions.md)); `type: note_routed` when parked.

Posture confirm: `type: project_posture`, `user_confirmed: true`. New Must after `signed_v1`: `type: scope_change` or reject — [project-posture.md](project-posture.md).

## Session completion signals

Treat as level/session done when user says (case-insensitive intent):

- "done", "that's enough", "good to proceed", "move on", "next level"
- "stop", "pause", "done for now" → checkpoint and exit (not level complete)

Do not advance a level while blocking clarifications remain unless user explicitly accepts gaps.
