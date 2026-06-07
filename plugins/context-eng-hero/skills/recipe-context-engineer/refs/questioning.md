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
  - **options:** Skill | Command | Agent | Rule | Workflow
- Pick narrowest fit per SKILL **Classify** table; if still ambiguous, one follow-up with two candidates only.

## Missing failure source (fix)

When user wants fix but supplied no audit/test report:

- **AskQuestion**
  - **question:** "What should we fix against?"
  - **header:** "Source"
  - **options:** Audit report | Test report | Symptom list
- Then collect the chosen source in the next turn (paste report, or list symptoms)—one item at a time.

## Fix vs redesign signal

Any outcome/capability change language → **fix-vs-redesign** gate before planning edits. See `fix-intake.md` for reject rules.

## Deferred fields

Outcome, audience, or failure mode may be explicitly deferred for **extract** drafts—list as open questions in output. Do not block create/fix on perfect clarify if user asked to ship a draft.
