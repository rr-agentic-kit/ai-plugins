# Chat orchestration

**Audience A:** Agent running **recipe-context-engineer**. **Audience B:** Humans authoring artifacts that embed tool guidance.

**Platform fact — commands cannot chain:** Cursor plugin commands are markdown prompts injected when the **user** picks a slash. There is **no API** for command A to execute command B. Slash names in command bodies are **user homework only**.

| Pattern | Works? | Use for |
|---------|--------|---------|
| User types a plugin slash | Yes | Explicit action |
| Command **Progress**: "Execute **Action:** … in skill **recipe-context-engineer**" + TodoWrite step ids | Yes | Black-box delegation |
| Command body lists `refs/actions/...` or `plugins/...` | **Avoid** | Leaks layout; skill **Run:** loads procedures |
| Command body: chain slashes as **only** routing | **No** | Forbidden |

Close surfaces: `close-contract.md`. Invoke modes: `skill-invocation.md` (single source).

---

## TodoWrite ownership

| Layer | TodoWrite |
|-------|-----------|
| **Action slash commands** | **Required:** Execute **Action** first; `merge: false` with step ids from that procedure |
| **Design command** | Default: no forced list. **Write branch:** design action + TodoWrite `design-1-classify` … `design-4-gates` |
| **Skill** (`recipe-context-engineer`) | Slash prompt wins Progress; does not auto-spawn todos on ambient invoke |
| **Authored workflows** | **Required:** each step `todo_id`; TodoWrite before step 1 |

---

## A. Agent operating this plugin

| Goal | Do in chat | Do not |
|------|------------|--------|
| Missing type or clarify fields | **AskQuestion** (2–4 options) | Open-ended ask when choices are enumerable |
| Research patterns before design | **Task** `subagentType: explore` (parallel OK) | Load entire repo in parent |

Routing and actions: skill **Actions** table + `gate-prompts.md`.

**AskQuestion:** classify/clarify, fix/redesign intake, workflow branches.

**Task / subagents:** isolated context; parallel = multiple Task calls in one message.

---

## B. Authors embedding orchestration

Required **## Orchestration** in **workflow** templates; optional elsewhere unless multi-step:

- **User invocation**: slash(es), required args
- **Agent tools**: when to use AskQuestion, TodoWrite, Task
- **Workflow execution**: TodoWrite one item per `todo_id` before step 1
- **Invoke modes:** see `skill-invocation.md`

**Rubric:** workflow `todo_id` and orchestration are **critical**; other types use judgment ids in `rubrics/*.rubric.md`.
