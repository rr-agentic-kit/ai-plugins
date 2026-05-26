# Action: fix (internal)

**Symptom-led** minimal repair.

## Load (Read)

- `fix-intake.md`
- `memory-hierarchy.md`
- `effective-writing.md`
- `communication-role-exhaustive.md` (only if comm/role dimensions implicated)
- `tooling-orchestration.md` (only if symptom maps to §6 / ignored capability)

## REQUIRED (command)

- Path to CLAUDE.md
- **Symptom** — what Claude did wrong, or which section fails (quote bullets or session example preferred)

## Stop

- Outcome/persona change → `/static-memory-design`
- Empty/missing file → `/static-memory-design`

## Steps

### Step 1: `1-fix-read`

- **Outcome:** Symptom mapped to sections; file read; fix scope only.
- **Done when:** `fix-intake.md` satisfied; no redesign scope.

### Step 2: `2-fix-diagnose`

- **Outcome:** Root cause identified with citations.
- **Done when:** Offending lines quoted; cause named (vague comm, project leak in global, stale command, missing trigger row, etc.).

### Step 3: `3-fix-plan`

- **Outcome:** Minimal edit plan.
- **Done when:** Each symptom maps to concrete bullet edits; comm/role gaps use exhaustive ref for **missing dimensions only**; §6 gaps use `tooling-orchestration.md` for missing triggers/modes only; no scope creep.

### Step 4: `4-fix-confirm`

- **Outcome:** User-approved patch.
- **Done when:** Patch summary shown; user approves.

### Step 5: `5-fix-write`

- **Outcome:** Minimal diff applied.
- **Done when:** Approved edits written only.

## Fix vs review

| | **fix** | **review** |
|---|---------|------------|
| Trigger | Symptom | Systematic audit |
| Scope | Minimal | All sections |
| Comm/role | Gap dimensions only | Default deep-dive if weak |
| §6 tooling | Gap triggers/modes only | Default deep-dive if &lt;2 real rows |

## Write gate

Confirm-before-write at step 4.

## Output

- Path
- Sections touched
- Symptom → change mapping (one line each)
