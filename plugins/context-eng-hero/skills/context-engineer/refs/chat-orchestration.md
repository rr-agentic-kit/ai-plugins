# Chat orchestration

**Audience A:** Agent running **context-engineer**. **Audience B:** Humans authoring artifacts that embed tool guidance.

**Platform fact — commands cannot chain:** Cursor plugin [commands are markdown prompts](https://cursor.com/docs/reference/plugins) injected when the **user** picks a slash. There is **no API** for command A to execute command B. Writing “run `/other`” inside a command is **user instruction only**, not automation.

| Pattern | Works? | Use for |
|---------|--------|---------|
| User types `/context-engineer-audit` | Yes | Explicit audit |
| Command body: “Execute **Action: audit** in skill **context-engineer**” | Yes | Black-box delegation |
| Command body lists `refs/actions/...` or `plugins/...` | **Avoid** | Leaks layout |
| Command body: “Invoke `/other-command`” as **only** routing | **No** | Forbidden orchestration |

Allowed: command tells the user what slash **they** may run next; skill **Classify** ends with **Next step (user)**.

Docs: [Agent Skills](https://cursor.com/docs/skills), [Subagents](https://cursor.com/docs/subagents).

---

## TodoWrite ownership

| Layer | TodoWrite |
|-------|-----------|
| **Action slash commands** (`context-engineer-create`, `-audit`, `-rewrite`, `-test`, `-diff`, `-extract`) | **Required:** `merge: false` at start; one todo per step id in `refs/actions/<verb>.md`; mark `completed` before advancing |
| **Design command** (`/context-engineer`) | Only if classify/clarify spans verifiable multi-step work (rare); otherwise no forced list |
| **Skill** (`context-engineer`) | Does **not** auto-spawn todos on ambient invoke; points to action slashes for tracked execution |
| **Authored workflows** | **Required** in template: each step `todo_id`; **Orchestration** instructs executor to TodoWrite before step 1; AskQuestion before branch-specific todos |

---

## A. Agent operating this plugin

| Goal | Do in chat | Do not |
|------|------------|--------|
| User wants audit/rewrite/test | State exact slash: `/context-engineer-audit` (Cursor) or `/context-eng-hero:context-engineer-audit` (Claude Code) | Run audit/rewrite from skill auto-invoke alone |
| Missing type or clarify fields | **AskQuestion** (2–4 options; `allow_multiple` when needed) | Open-ended ask when choices are enumerable |
| User ran an action slash | **TodoWrite** per command **Progress** block | Skip todos or batch-complete without doing steps |
| Research patterns before design | **Task** `subagentType: explore` (parallel OK) | Load entire repo in parent |
| This plugin’s actions | User slash → command delegates to **Action:** in **context-engineer** | Commands listing `refs/actions/*` in user-facing text |

**AskQuestion** (Cursor): structured multiple-choice; use in classify/clarify and workflow branches.

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

### This plugin’s commands

| Slash (Cursor) | Role |
|----------------|------|
| `/context-engineer` | Classify + Clarify; **Next step (user)** only |
| `/context-engineer-create` | Action: create + Progress todos |
| `/context-engineer-extract` | Action: extract + Progress todos |
| `/context-engineer-audit` | Action: audit + Progress todos |
| `/context-engineer-rewrite` | Action: rewrite + Progress todos |
| `/context-engineer-test` | Action: test + Progress todos |
| `/context-engineer-diff` | Action: diff + Progress todos |

Claude Code: prefix `/context-eng-hero:` on each name above.
