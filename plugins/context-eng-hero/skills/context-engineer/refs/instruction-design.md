# Instruction design (context artifacts)

Principles for **skills**, **commands**, **agents**, **rules**, and **workflows**. Load with **create**, **extract**, **fix**, **redesign**, and **design assist write** (`refs/actions/design.md`).

## Signal vs noise

- **Signal**: constraints the agent cannot infer (policy, gates, exact formats, stop rules).
- **Noise**: generic encouragement, repeated restatements of the obvious, or prose that duplicates tool docs.

Cut noise until every paragraph changes behavior or discovery.

- **Cross-file echo**: if a ref's **Load** chain includes file X, do not restate X's constraints in the loading file. The agent reads both; the restatement is pure noise.

## Forcing function

When a choice is enumerable, prefer a **structured question** (e.g. AskQuestion in Cursor) over an open-ended “what do you want?”.

When work spans multiple **verifiable** steps:

- **Action slash commands** → executor uses **TodoWrite** (`merge: false`) with ids from `refs/actions/<verb>.md` (**Progress** block in each command).
- **Workflows** → each step row has `todo_id`; **Orchestration** requires TodoWrite before step 1.
- **Design-only skill invoke** → no forced todo list unless the user chose an action slash.

Do not rely on long inline checklists only the model sees when the platform can show todos.

## Layer separation

| Layer | Holds |
|-------|--------|
| **Skill** | Judgment, classification, reusable procedure, progressive disclosure via refs |
| **Command** | Slash contract: required inputs, **Progress** + delegation to skill **Action**, output shape—no internal `refs/` paths in user-facing command bodies |
| **Refs** | Templates, rubrics, long checklists—loaded only when an Action runs |

Do not duplicate the same policy in three places; **link** the canonical ref once.

## Micro examples (pattern)

**Bad:** “Be helpful and write good code.”  
**Good:** “Stop after listing changed files; do not commit unless the user asked.”

**Bad:** “Consider security.”  
**Good:** “Reject if the diff adds `eval(` or logs secrets; cite line.”

**Bad:** “Use best practices.”  
**Good:** “Match surrounding file’s import style (top-level only).”
