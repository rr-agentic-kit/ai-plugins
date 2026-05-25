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

### Step 4: `create-4-gates`

- **Outcome:** Shared write gates passed or write blocked.
- **Done when:** All four gates in `refs/actions/shared-write-gates.md` completed in order (static → reflect → pre-ship → write).

## Stop

Do not bypass reflection or pre-ship. Do not write outside agreed plugin-relative paths.
