# Chat orchestration

**Audience A:** Agent running **context-engineer**. **Audience B:** Humans authoring artifacts that embed tool guidance.

**Platform fact — commands cannot chain:** Cursor plugin [commands are markdown prompts](https://cursor.com/docs/reference/plugins) injected when the **user** picks a slash. There is **no API** for command A to execute command B. Writing “run `/other`” inside a command is **user instruction only**, not automation.

| Pattern | Works? | Use for |
|---------|--------|---------|
| User types `/context-engineer-audit` | Yes | Explicit audit |
| Command **Progress**: “Execute **Action:** … in skill **context-engineer**” first, then TodoWrite step ids | Yes | Black-box delegation |
| Command body lists `refs/actions/...` or `plugins/...` | **Avoid** | Leaks layout; skill **Run:** loads internal procedures |
| Command body: “Invoke `/other-command`” as **only** routing | **No** | Forbidden orchestration |

Allowed: command tells the user what slash **they** may run next; skill **Classify** ends with **Next step (user)**.

Docs: [Agent Skills](https://cursor.com/docs/skills), [Subagents](https://cursor.com/docs/subagents).

---

## TodoWrite ownership

| Layer | TodoWrite |
|-------|-----------|
| **Action slash commands** (`context-engineer-create`, `-audit`, `-fix`, `-redesign`, `-test`, `-diff`, `-extract`) | **Required:** Execute **Action** first (skill **Run:** loads procedure); `merge: false` TodoWrite with step ids matching that procedure; mark `completed` before advancing |
| **Design command** (`/context-engineer`) | Default: no forced list. **Write branch:** design assist write in skill **context-engineer** + TodoWrite `design-1-classify` … `design-4-gates` |
| **Skill** (`context-engineer`) | **Harness precedence:** slash prompt wins Progress/inputs/output; does **not** auto-spawn todos on ambient invoke |
| **Authored workflows** | **Required** in template: each step `todo_id`; **Orchestration** instructs executor to TodoWrite before step 1; AskQuestion before branch-specific todos |

---

## A. Agent operating this plugin

| Goal | Do in chat | Do not |
|------|------------|--------|
| Missing type or clarify fields | **AskQuestion** (2–4 options; `allow_multiple` when needed) | Open-ended ask when choices are enumerable |
| Research patterns before design | **Task** `subagentType: explore` (parallel OK) | Load entire repo in parent |

Routing, harness precedence, and slash names: skill **context-engineer** (**Routing**, **Actions**, **Invocation**). Commands must not list `refs/actions/*` in user-facing bodies.

**AskQuestion** (Cursor): structured multiple-choice; use in classify/clarify, fix/redesign intake, and workflow branches.

**TodoWrite**: owned by **action commands** and **workflow execution** as above—not optional for those paths.

**Task / subagents**: isolated context; parallel = multiple Task calls in one message.

**Other skills**: discovery via `description`; manual `/skill` or `@skill`. `disable-model-invocation: true` → slash-only, like action commands.

---

## B. Authors embedding orchestration

Required **## Orchestration** in **workflow** templates; optional elsewhere unless multi-step:

- **User invocation**: slash(es), required args
- **Agent tools**: when to use AskQuestion, TodoWrite, Task
- **Workflow execution**: TodoWrite one item per `todo_id` in **Steps** before step 1
- **disable-model-invocation**: `true` for action-like artifacts; default false for judgment skills

**Rubric:** workflow orchestration and per-step `todo_id` are **critical**; other types use judgment ids in `*.audit-rubric.md`.

### Invocation matrix

| Mechanism | User | Agent | Author sets |
|-----------|------|-------|-------------|
| Plugin command | `/name` | Prompt → skill Action + Progress todos | `commands/*.md` |
| Skill auto | natural language | matches `description` | rich WHEN clause |
| Skill manual | `/name` or `@name` | explicit | optional `disable-model-invocation` |
| Subagent | `/agent` or Task | sub-run | agent markdown |
| AskQuestion | UI | tool | procedure step / workflow branch |
| TodoWrite | UI list | tool | action commands + workflow execution |

Slash map: skill **context-engineer** **Actions** table.
