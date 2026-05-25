# Action: redesign (internal)

Change what the artifact **does**: outcome, audience, capabilities, or contracts. Structural edits allowed; document tradeoffs.

## Load (Read)

- `redesign-intake.md`
- `instruction-design.md`
- `frontmatter-schemas.md`
- `chat-orchestration.md`
- Matching artifact template
- Optional prior **diff** report if user compared two versions

## Steps

### Step 1: `redesign-1-clarify`

- **Outcome:** Delta brief and constraints are explicit.
- **Done when:** `redesign-intake.md` satisfied; breaking-change stance recorded; no silent scope creep beyond delta brief.

### Step 2: `redesign-2-plan`

- **Outcome:** Impact plan lists section/contract changes and tradeoffs.
- **Done when:** Each delta maps to concrete edits (add/remove/revise sections, frontmatter, stop rules); optional diff notes referenced; old audit FAILs not treated as mandatory fix list.

### Step 3: `redesign-3-apply`

- **Outcome:** Redesigned draft applied.
- **Done when:** All planned edits applied in memory or working copy.

### Step 4: `redesign-4-gates`

- **Outcome:** Shared write gates passed or write blocked; user told to re-audit when write succeeds.
- **Done when:** All four gates in `refs/actions/shared-write-gates.md` completed in order (static → reflect → pre-ship → write); output includes **Recommended next step (user):** run `/context-engineer-audit` on the same path (platform cannot chain).

## Stop

Quality bar unchanged—static + reflection + pre-ship required before write. Do not claim parity with old audit PASS/FAIL lists; recommend fresh audit after write.
