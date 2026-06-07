# Action: create (internal)

## Load (Read)

- `disambiguation.md`
- `advisory.md`
- `ui-brand.md`
- `gate-prompts.md`
- `questioning.md`
- `frontmatter-schemas.md`
- `instruction-design.md`
- `chat-orchestration.md`
- Matching artifact template: `skill.template.md` | `command.template.md` | `agent.template.md` | `rule.template.md` | `workflow.template.md`

## Steps

### Step 1: `create-1-classify`

- **Outcome:** Artifact type is the narrowest fit.
- **Done when:** Type named via Classify + `questioning.md` if unknown—no draft started until type known.
- **Banner:** `CE ► CREATE` per `ui-brand.md`.

### Step 2: `create-2-clarify`

- **Outcome:** Outcome, audience, and failure mode are resolved (or explicitly deferred with open questions listed).
- **Done when:** Clarify fields answered per `questioning.md` (one question at a time); no REQUIRED hard-stop.

### Step 3: `create-3-draft`

- **Outcome:** Draft file content from template; `<!-- REQUIRED -->` markers replaced.
- **Done when:** Full draft in memory; workflow steps include `todo_id` column if type is workflow.

### Step 4: `create-4-gates`

- **Outcome:** Shared write gates passed or write blocked.
- **Done when:** All four gates in `refs/actions/shared-write-gates.md` completed in order (static → reflect → pre-ship → write).

### Step 5: `create-5-close`

- **Outcome:** User routed to next action or done.
- **Done when:** **post-create-routing** AskQuestion per `gate-prompts.md`; on selection, skill continues to routed action; else **Next Up** block per `ui-brand.md`.

## Stop

Do not bypass reflection or pre-ship. Do not write outside agreed plugin-relative paths.
