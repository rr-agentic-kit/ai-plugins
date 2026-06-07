# Action: fix (internal)

Apply **minimal** edits so the artifact matches **existing** intent. Prefer audit- or test-led FAIL lists.

## Load (Read)

- `ui-brand.md`
- `gate-prompts.md`
- `questioning.md`
- `fix-intake.md`
- `instruction-design.md`
- `frontmatter-schemas.md`
- `chat-orchestration.md`
- Matching artifact template
- Prior audit or test report if user supplied

## Steps

### Step 1: `fix-1-read`

- **Outcome:** Target file and failure list are known; scope is fix-only.
- **Done when:** Path and failure source resolved via `questioning.md` + `fix-intake.md` (no REQUIRED hard-stop); file read; every FAIL id (all severities) or symptom→edit mapping captured; outcome-preservation confirmed or **fix-vs-redesign** gate run → redesign if outcome change.
- **Banner:** `CE ► FIX` per `ui-brand.md`.

### Step 2: `fix-2-plan`

- **Outcome:** Minimal diff plan addresses **every** listed FAIL or mapped symptom.
- **Done when:** Each failed check id maps to a concrete edit; no unrelated refactors; no capability/outcome changes.

### Step 3: `fix-3-apply`

- **Outcome:** Edits applied to draft.
- **Done when:** All planned fixes applied in memory or working copy.

### Step 4: `fix-4-gates`

- **Outcome:** Shared write gates passed or write blocked.
- **Done when:** All four gates in `refs/actions/shared-write-gates.md` completed in order (static → reflect → pre-ship → write).

### Step 5: `fix-5-close`

- **Outcome:** User routed to next action or done.
- **Done when:** **post-fix-routing** AskQuestion per `gate-prompts.md`; on selection, skill continues to routed action; else **Next Up** block per `ui-brand.md`.

## Stop

No scope expansion. When audit-led, fix **every** FAIL (critical, major, minor)—no "critical only" shortcut.
