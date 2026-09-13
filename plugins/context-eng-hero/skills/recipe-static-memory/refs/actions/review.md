# Action: review (internal)

**Section-by-section** walkthrough of existing always-on / situational instruction packs.

## Load (Read)

- `memory-hierarchy.md`
- `agents-md-bridge.md`
- `situation-groups.md` (project; when packs or bloat present)
- `user-sections-template.md` or `project-sections-template.md` (match file scope)
- `communication-role-exhaustive.md` (deep-dive only)
- `tooling-orchestration.md` (when §6 Tooling & agents missing/weak)
- `effective-writing.md`
- `user-global-synthesis.md` (user-global — leak check)

## REQUIRED (command)

- Path to existing always-on file (`AGENTS.md` or user-global equivalent); note sibling `CLAUDE.md` / `.agents/` if present

## Stop

Always-on file missing or empty → **Next step (user):** `/static-memory-design`.

## Steps

### Step 1: `1-review-read`

- **Outcome:** Files mapped to template; issues flagged.
- **Done when:** Sections mapped; low-leverage / docs-dump / stale / project-leak noted; `@` of situational packs flagged FAIL; pack names checked against `situation-groups.md` (no assumed catalog).

### Step 2: `2-review-walk`

- **Outcome:** Each section gated by user choice.
- **Done when:** For **each** section in template order that exists or should: (1) show current text or `(missing)`; (2) **AskQuestion:** Accept / Edit inline / Deep-dive / **Delete low-leverage** — unless user explicitly batch-approved all sections upfront.

**Mandatory Deep-dive default** for **Communication** and **Role** when missing, weak, or &lt;3 testable bullets (user-global).

**Mandatory Deep-dive default** for **Tooling & agents** (§6) when missing, &lt;2 rows with real triggers, or only vague prose (“use skills when relevant”).

### Step 3: `3-review-deep`

- **Outcome:** Exhaustive questions for deep-dive sections.
- **Done when:** Communication/Role use `communication-role-exhaustive.md` (implicated dimensions only unless full redesign of persona); §6 uses `tooling-orchestration.md`; bloat/pack decisions use inclusion bar + `situation-groups.md`; other sections get targeted questions only.

### Step 4: `4-review-confirm`

- **Outcome:** Consolidated change proposal.
- **Done when:** Diff-style summary shown (including deletions and pack create/merge/drop); user approves writes.

### Step 5: `5-review-write`

- **Outcome:** Approved edits only on disk.
- **Done when:** Only approved sections/packs written or deleted; updated bullets shown after each section edit before advancing (during walk) or in summary before write.

## Section walk rules

- No batch-approve whole file without explicit user opt-in.
- After each section edit during walk, show updated bullets before next section.
- **Delete** bullets that fail the 90% bar—do not keep for completeness.
- Prefer pointer to README/CONTRIBUTING over absorbing docs.

## Write gate

Confirm-before-write at step 4 — no plugin shared-write-gates.

## Output

- Paths reviewed
- Sections touched (accept / edit / deep-dive / delete)
- Pack changes if any
- Pre-write summary of changes
