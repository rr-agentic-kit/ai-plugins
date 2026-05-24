# Action: create (internal)

## Load (Read)

- `frontmatter-schemas.md`
- `instruction-design.md`
- `chat-orchestration.md`
- Matching artifact template: `skill.template.md` | `command.template.md` | `agent.template.md` | `rule.template.md` | `workflow.template.md`

## Steps

### Step 1: `create-1-classify`

- **Outcome:** Artifact type is the narrowest fit.
- **Done when:** Type named; if unknown, stopped with questions—no draft started.

### Step 2: `create-2-clarify`

- **Outcome:** Outcome, audience, and failure mode are resolved (or explicitly deferred with open questions listed).
- **Done when:** SKILL **Clarify** fields answered or AskQuestion completed.

### Step 3: `create-3-draft`

- **Outcome:** Draft file content from template; `<!-- REQUIRED -->` markers replaced.
- **Done when:** Full draft in memory; workflow steps include `todo_id` column if type is workflow.

### Step 4: `create-4-pre-ship`

- **Outcome:** Pre-ship gate result known.
- **Done when:** `pre-ship-checklist.md` run line by line; §1 schema items satisfied via static script when applicable; table with PASS/FAIL per item.

### Step 5: `create-5-write`

- **Outcome:** File written or blocked with report.
- **Done when:** If pre-ship PASSED: file at user-approved plugin-relative path; if FAILED: `PRE-SHIP FAILED` + table, draft in chat only.

## Stop

Do not bypass pre-ship. Do not write outside agreed plugin-relative paths.
