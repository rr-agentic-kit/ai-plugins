# Action: review (internal)

**Section-by-section** walkthrough of an existing CLAUDE.md.

## Load (Read)

- `memory-hierarchy.md`
- `user-sections-template.md` or `project-sections-template.md` (match file scope)
- `communication-role-exhaustive.md` (deep-dive only)
- `tooling-orchestration.md` (when §6 Tooling & agents missing/weak)
- `effective-writing.md`
- `user-global-synthesis.md` (user-global — leak check)
- `agents-md-bridge.md` (project)

## REQUIRED (command)

- Path to existing CLAUDE.md (user-global or project)

## Stop

File missing or empty → **Next step (user):** `/static-memory-design`.

## Steps

### Step 1: `1-review-read`

- **Outcome:** File mapped to template; issues flagged.
- **Done when:** Sections mapped; stale/project-leak noted for user-global.

### Step 2: `2-review-walk`

- **Outcome:** Each section gated by user choice.
- **Done when:** For **each** section in template order: (1) show current text or `(missing)`; (2) **AskQuestion:** Accept / Edit inline / Deep-dive — unless user explicitly batch-approved all sections upfront.

**Mandatory Deep-dive default** for **Communication** and **Role** when missing, weak, or &lt;3 testable bullets.

**Mandatory Deep-dive default** for **Tooling & agents** (§6) when missing, &lt;2 rows with real triggers, or only vague prose (“use skills when relevant”).

### Step 3: `3-review-deep`

- **Outcome:** Exhaustive questions for deep-dive sections.
- **Done when:** Communication/Role use `communication-role-exhaustive.md` (implicated dimensions only unless full redesign of persona); §6 uses `tooling-orchestration.md`; other sections get targeted questions only.

### Step 4: `4-review-confirm`

- **Outcome:** Consolidated change proposal.
- **Done when:** Diff-style summary shown; user approves writes.

### Step 5: `5-review-write`

- **Outcome:** Approved edits only on disk.
- **Done when:** Only approved sections written; updated bullets shown after each section edit before advancing (during walk) or in summary before write.

## Section walk rules

- No batch-approve whole file without explicit user opt-in.
- After each section edit during walk, show updated bullets before next section.

## Write gate

Confirm-before-write at step 4 — no plugin shared-write-gates.

## Output

- Path reviewed
- Sections touched (accept / edit / deep-dive)
- Pre-write summary of changes
