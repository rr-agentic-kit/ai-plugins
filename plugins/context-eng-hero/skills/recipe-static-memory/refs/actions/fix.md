# Action: fix (internal)

**Symptom-led** minimal repair.

## Load (Read)

- `fix-intake.md`
- `memory-hierarchy.md`
- `agents-md-bridge.md`
- `user-global-multi-harness.md` (when path is user-global or symptom is harness-specific)
- `effective-writing.md`
- `situation-groups.md` (only if symptom maps to missing pack / wrong trigger / pack bloat)
- `communication-role-exhaustive.md` (only if comm/role dimensions implicated)
- `tooling-orchestration.md` (only if symptom maps to §6 / ignored capability)
- `user-global-synthesis.md` (only if user-global leak / wrong home file)

## REQUIRED (command)

- Path to always-on file (`AGENTS.md`, `~/.agents/AGENTS.md`, or user-global equivalent)
- **Symptom** — what the agent did wrong, or which section fails (quote bullets or session example preferred)

## Stop

- Outcome/persona change → `/static-memory-design`
- Empty/missing always-on file → `/static-memory-design`

## Steps

### Step 1: `1-fix-read`

- **Outcome:** Symptom mapped; files read; fix scope only.
- **Done when:** `fix-intake.md` satisfied; no redesign scope; for user-global, related adapters/overlays discovered when symptom may be harness-specific.

### Step 2: `2-fix-diagnose`

- **Outcome:** Root cause identified with citations.
- **Done when:** Offending lines quoted; cause named — e.g. vague always-on, missing Read trigger, belongs in docs, low-leverage bloat, `@` of situational pack, stale command, missing tooling trigger, harness-only rule in wrong file (SoT vs overlay vs adapter mirror).

### Step 3: `3-fix-plan`

- **Outcome:** Minimal edit plan.
- **Done when:** Each symptom maps to concrete bullet edits in the **correct home** (shared SoT **or** `*.specific.md` **or** thin adapter stub **or** trigger/pack **or** “defer to docs”); no new pack unless `situation-groups.md` justifies; comm/role gaps use exhaustive ref for **missing dimensions only**; §6 gaps use `tooling-orchestration.md` for missing triggers/modes only; harness-specific fixes do not land in the wrong layer; no scope creep.

### Step 4: `4-fix-confirm`

- **Outcome:** User-approved patch.
- **Done when:** Patch summary shown (paths + layers); user approves.

### Step 5: `5-fix-write`

- **Outcome:** Minimal diff applied.
- **Done when:** Approved edits written only.

## Fix vs review

| | **fix** | **review** |
|---|---------|------------|
| Trigger | Symptom | Systematic audit |
| Scope | Minimal | All sections + packs (+ adapters/overlays when user-global) |
| Comm/role | Gap dimensions only | Default deep-dive if weak |
| §6 tooling | Gap triggers/modes only | Default deep-dive if &lt;2 real rows |
| Harness overlay | Only if symptom is harness-specific | Walk overlays when discovered |
| Low-leverage | Delete only if it causes the symptom | May delete freely |

## Write gate

Confirm-before-write at step 4.

## Output

- Path(s) (SoT / overlay / adapter as touched)
- Sections / packs / overlays touched
- Symptom → change mapping (one line each)
