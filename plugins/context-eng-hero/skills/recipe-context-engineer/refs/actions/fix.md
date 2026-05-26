# Action: fix (internal)

Apply **minimal** edits so the artifact matches **existing** intent. Prefer audit- or test-led FAIL lists.

## Load (Read)

- `fix-intake.md`
- `instruction-design.md`
- `frontmatter-schemas.md`
- `chat-orchestration.md`
- Matching artifact template
- Prior audit or test report if user supplied

## Steps

### Step 1: `fix-1-read`

- **Outcome:** Target file and failure list are known; scope is fix-only.
- **Done when:** `fix-intake.md` satisfied; file read; every FAIL id (all severities) or symptom→edit mapping captured; outcome-preservation confirmed or user routed to redesign.

### Step 2: `fix-2-plan`

- **Outcome:** Minimal diff plan addresses **every** listed FAIL or mapped symptom.
- **Done when:** Each failed check id maps to a concrete edit; no unrelated refactors; no capability/outcome changes.

### Step 3: `fix-3-apply`

- **Outcome:** Edits applied to draft.
- **Done when:** All planned fixes applied in memory or working copy.

### Step 4: `fix-4-gates`

- **Outcome:** Shared write gates passed or write blocked.
- **Done when:** All four gates in `refs/actions/shared-write-gates.md` completed in order (static → reflect → pre-ship → write).

## Stop

No scope expansion. When audit-led, fix **every** FAIL (critical, major, minor)—no “critical only” shortcut.
