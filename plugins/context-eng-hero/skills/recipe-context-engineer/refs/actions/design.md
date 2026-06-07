# Action: design assist write (internal)

Conditional procedure when **`/context-engineer`** or skill **Classify** + **Clarify** ends with writing a file this turn. Default design assist (no write) does **not** load this file.

## Load (Read)

- `disambiguation.md`
- `advisory.md`
- `questioning.md`
- `instruction-design.md`
- `frontmatter-schemas.md`
- `chat-orchestration.md`
- Matching artifact template: `skill.template.md` | `command.template.md` | `agent.template.md` | `rule.template.md` | `workflow.template.md`

## Triggers (all required)

- User explicitly requests writing a file (path stated or approved after one ask).
- Classify/clarify sufficient to draft, or open questions listed explicitly in output.

If the user only wanted a new file and did not insist on this slash, prefer **AskQuestion**: “Finish here or run `/context-engineer-create`?”

## Steps

### Step 1: `design-1-classify`

- **Outcome:** Artifact type is the narrowest fit.
- **Done when:** SKILL **Classify** satisfied; type named (may already be done earlier this turn).

### Step 2: `design-2-clarify`

- **Outcome:** Outcome, audience, and failure mode resolved or open questions listed.
- **Done when:** SKILL **Clarify** satisfied; ready to draft or gaps explicit.

### Step 3: `design-3-draft`

- **Outcome:** Template-shaped draft at approved plugin-relative path.
- **Done when:** Full draft in memory/working copy; `<!-- REQUIRED -->` markers replaced; workflow steps include `todo_id` if type is workflow.

### Step 4: `design-4-gates`

- **Outcome:** Shared write gates passed or write blocked.
- **Done when:** All four gates in `refs/actions/shared-write-gates.md` completed in order (static → reflect → pre-ship → write).

## Stop

Do not skip gates because “it’s only design assist.” No silent invention of missing business facts—list open questions if clarify incomplete.
