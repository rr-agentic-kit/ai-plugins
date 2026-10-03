# Action: review (internal)

**Section-by-section** walkthrough of existing always-on / situational instruction packs.

## Load (Read)

- `memory-hierarchy.md`
- `agents-md-bridge.md`
- `user-global-multi-harness.md` (user-global — adapters/overlays/migration)
- `situation-groups.md` (project; when packs or bloat present)
- `user-sections-template.md` or `project-sections-template.md` (match file scope)
- `communication-role-exhaustive.md` (deep-dive only)
- `tooling-orchestration.md` (when §6 Tooling & agents missing/weak)
- `effective-writing.md`
- `user-global-synthesis.md` (user-global — leak + overlay home check)

## REQUIRED (command)

- Path to existing always-on file (`AGENTS.md`, `~/.agents/AGENTS.md`, or legacy user-global equivalent); note sibling pointers/adapters / `.agents/` / overlays if present

## Stop

Always-on file missing or empty → **Next step (user):** `/static-memory-design`.

## Steps

### Step 1: `1-review-read`

- **Outcome:** Files mapped to template; issues flagged.
- **Done when:**
  - Sections mapped; low-leverage / docs-dump / stale / project-leak noted
  - `@` of situational packs flagged FAIL
  - Pack names checked against `situation-groups.md` (no assumed catalog)
  - **user-global:** discover adapters (`~/.claude/CLAUDE.md`, `~/.cursor/rules/user-global.mdc`, Codex/Copilot stubs) and overlays (`*.specific.md`); flag SoT body mirrors in adapters; flag Claude-only legacy SoT under `~/.claude/` for migration; flag harness-only content stuck in shared SoT

### Step 2: `2-review-walk`

- **Outcome:** Each section gated by user choice.
- **Done when:** For **each** section in template order that exists or should: (1) show current text or `(missing)`; (2) **AskQuestion:** Accept / Edit inline / Deep-dive / **Delete low-leverage** — unless user explicitly batch-approved all sections upfront.

**Mandatory Deep-dive default** for **Communication** and **Role** when missing, weak, or &lt;3 testable bullets (user-global).

**Mandatory Deep-dive default** for **Tooling & agents** (§6) when missing, &lt;2 rows with real triggers, or only vague prose (“use skills when relevant”).

**user-global extras:** walk **Harness overlays** for each discovered/selected harness; challenge adapter mirrors → thin stub (user confirm before replace).

### Step 3: `3-review-deep`

- **Outcome:** Exhaustive questions for deep-dive sections.
- **Done when:** Communication/Role use `communication-role-exhaustive.md` (implicated dimensions only unless full redesign of persona); §6 uses `tooling-orchestration.md`; overlay sections get harness-only questions (not a second comm/role interview); bloat/pack decisions use inclusion bar + `situation-groups.md`; other sections get targeted questions only.

### Step 4: `4-review-confirm`

- **Outcome:** Consolidated change proposal.
- **Done when:** Diff-style summary shown (including deletions, pack create/merge/drop, adapter stub replacements, overlay splits/moves); user approves writes for the whole set touched.

### Step 5: `5-review-write`

- **Outcome:** Approved edits only on disk.
- **Done when:** Only approved sections/packs/adapters/overlays written or deleted; updated bullets shown after each section edit before advancing (during walk) or in summary before write.

## Section walk rules

- No batch-approve whole file without explicit user opt-in.
- After each section edit during walk, show updated bullets before next section.
- **Delete** bullets that fail the 90% bar—do not keep for completeness.
- Prefer pointer to README/CONTRIBUTING over absorbing docs.
- Harness-specific symptoms/content → correct file (`*.specific.md` or matching adapter stub), not blindly into SoT.

## Write gate

Confirm-before-write at step 4 — no plugin shared-write-gates.

## Output

- Paths reviewed (SoT + adapters + overlays when user-global)
- Sections touched (accept / edit / deep-dive / delete)
- Pack / overlay / adapter changes if any
- Pre-write summary of changes
