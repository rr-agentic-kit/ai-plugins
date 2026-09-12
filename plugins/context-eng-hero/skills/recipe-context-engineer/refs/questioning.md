# Questioning (graceful intake)

Rules for resolving missing context **without** hard-blocking on REQUIRED lists. Used by skill intake and action step 1 where noted.

## Core rules

1. **One question at a time** — never batch unrelated asks in one turn.
2. **Classify before action** — if artifact type is unknown, resolve type before asking what to do.
3. **Never block on REQUIRED** — offer paths forward instead of stopping with a bullet list of missing fields.
4. **Prefer AskQuestion** when choices are enumerable (2–4 options); use open text only when options cannot be listed.
5. **Use open context first** — read the user message, @-attached files, and editor selection before asking.

## Missing path

When no plugin-relative path is known:

- **AskQuestion**
  - **question:** "Which artifact should we work on?"
  - **header:** "Target"
  - **options:** Paste path | Describe location | Skip for now
- **Route map:**
  - Paste path → user supplies path in follow-up; continue
  - Describe location → user describes; agent locates or proposes candidate; confirm once
  - Skip for now → **classify** + **clarify** only (design assist); no audit/fix/create until path known

## Missing action

When path or goal is known but verb is unclear → **action-routing** in `gate-prompts.md`.

## Missing artifact type

When action needs type (create, audit rubric) and type is unclear:

- **AskQuestion**
  - **question:** "What kind of context artifact is this?"
  - **header:** "Type"
  - **options:** Skill | Skill+Ref | Ref file | Command | Agent | Rule | Workflow
- Pick narrowest fit per `classify.md`; if still ambiguous, one follow-up with two candidates only.

## Missing invoke mode (skills — create/fix/design)

When authoring a skill and mode is unclear:

- **AskQuestion**
  - **question:** "How should this skill be invoked?"
  - **header:** "Invoke mode"
  - **options:** Auto-invoke (ambient match) | Slash-or-parent (self-invoke) | Background (agent auto-pull, hide / on Claude)
- Route per `skill-invocation.md`; draft `description` and flags only after selection.

## Missing failure source (fix)

When user wants fix but supplied no audit/test report / learn handover:

- **AskQuestion**
  - **question:** "What should we fix against?"
  - **header:** "Source"
  - **options:** Audit report | Test report | Learn handover | Symptom list
- Then collect the chosen source in the next turn (paste report, or list symptoms)—one item at a time.

## Missing skill path (learn)

When action is learn and no plugin-relative skill path is known → same AskQuestion as **Missing path** above; do not proceed to investigate until path bound.

## Optional problem-statement overlay (learn)

When miss is thin in chat (thin patch **or** thin friction signal) or user wants to seed diagnosis:

- **AskQuestion**
  - **question:** "Add a short problem statement for this miss?"
  - **header:** "Miss"
  - **options:** This chat only | Add problem statement | Both
- Route: chat-only → continue; add / both → one open-text capture, then bind as miss overlay per `learn-intake.md`.

## Contradiction detection

When the same message contains conflicting signals (see `disambiguation.md`):

- **Conflicting verbs** — e.g. "fix the typos but change the outcome" → route to **fix-vs-redesign** gate before planning
- **Outcome vs wording** — polish language that also changes capability → **fix-vs-redesign** gate
- **Type vs action mismatch** — e.g. "audit and rewrite" → one AskQuestion to pick primary intent
- **Resolution:** one AskQuestion round max; if unresolved → conservative default (fix < redesign < create) per `disambiguation.md`, or hard stop if unsafe

Do not proceed to Act while contradictions remain unaddressed.

## Unclear instruction

Distinguish **missing** (field absent) from **unclear** (user said something but intent cannot be parsed):

| Case | Treatment |
|------|-----------|
| Enumerable interpretations (2–4) | **AskQuestion** with labeled options |
| Non-enumerable / open-ended | One open-text ask, then proceed with stated assumption |
| Partial signal (ambiguous, not unclear) | State assumption inline per `disambiguation.md`; do NOT ask |

Retry cap: 1 AskQuestion + 1 open ask for unclear; then proceed.

## Fix vs redesign signal

Any outcome/capability change language → **fix-vs-redesign** gate before planning edits. See `fix-intake.md` for reject rules.

## Deferred fields

Outcome, audience, or failure mode may be explicitly deferred for **extract** drafts—list as open questions in output. Do not block create/fix on perfect clarify if user asked to ship a draft.
