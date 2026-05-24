# Action: rewrite (internal)

## Load (Read)

- `instruction-design.md`
- `frontmatter-schemas.md`
- `pre-ship-checklist.md`
- `chat-orchestration.md`
- Matching artifact template
- Prior audit report if user supplied (required input when fixing audit findings)

## Steps

### Step 1: `rewrite-1-read`

- **Outcome:** Target file and failure list are known.
- **Done when:** File read; if audit report provided, every FAIL id (critical, major, minor) listed as fix targets; if no audit, user’s explicit fix list captured.

### Step 2: `rewrite-2-plan`

- **Outcome:** Minimal diff plan addresses **every** FAIL (all severities).
- **Done when:** Each failed check id maps to a concrete edit; no unrelated refactors.

### Step 3: `rewrite-3-apply`

- **Outcome:** Edits applied to draft.
- **Done when:** All planned fixes applied in memory or working copy.

### Step 4: `rewrite-4-static`

- **Outcome:** Static checks pass on revised content.
- **Done when:** From plugin root, after PyYAML bootstrap if needed (`python-runtime.md`), `python3 scripts/audit_static.py . <relative-path>` run; all static rows PASS or fixes applied until PASS.

### Step 5: `rewrite-5-pre-ship`

- **Outcome:** Human-judgment pre-ship items verified.
- **Done when:** `pre-ship-checklist.md` run; any FAIL blocks write.

### Step 6: `rewrite-6-write`

- **Outcome:** Final artifact delivered or blocked.
- **Done when:** If PASSED: patch summary + write to approved path; if FAILED: `PRE-SHIP FAILED`, prior disk state unchanged unless user wants draft-only.

## Stop

No scope expansion. Fix **every** audit FAIL when an audit report was the input—no “critical only” shortcut.
