# Tooling orchestration

**Load for:** user-global **design** (mandatory mini-interview after comm/role checkpoint **C**); **review** when §6 Tooling & agents is missing/weak; **fix** when symptom = “didn’t use skill X / wrong tool / improvised instead of …”.

## Design principle: ask for situations, not catalogs

| Avoid | Prefer |
|-------|--------|
| “List all your skills” | “What phrases or tasks should always pull a specific capability?” |
| “Be proactive with tools” | “When I say `ship it`, run review-and-ship skill before commit” |
| Naming 40 installed skills | 5–15 high-signal triggers; `N/A — no auto-invoke` per category |

**Phase A (agent-only, optional):** If cwd has `.cursor/plugins`, `skills/`, or MCP config, skim names/descriptions to **suggest** mappings—user confirms/rejects; never auto-write unconfirmed triggers.

## Interview checkpoint (group C)

After groups **A** (Communication) and **B** (Role), run **Tooling orchestration** (resumable with same **Interview state** block; set `group_done: C` when complete).

**Phase B — situation buckets** (AskQuestion per bucket; pre-fill from initial prompt):

1. **Dependencies & versions** — bump/upgrade/security audit → skill/MCP?
2. **CI / pipelines / deploy** — debug failed build, run pipeline → skill/MCP?
3. **Git / MR / review** — push, PR, review comments, merge conflicts → skill/agent?
4. **Code quality** — refactor, Sonar, pre-commit, “review this” → skill/agent?
5. **Exploration** — large unknown codebase → `Task explore` vs inline read/grep?
6. **Docs & libraries** — framework/API questions → Context7 / docs MCP first?
7. **Domain plugins** — user-named plugins → slash vs ambient skill load?
8. **Never auto** — capabilities to use only when explicitly named

**Phase C — encode mode per row** (force explicit choice):

| Mode | Meaning | Example bullet |
|------|---------|----------------|
| `load-first` | Read skill / check MCP schema before planning | “On dependency bump requests, load `bump-versions` skill first” |
| `invoke` | Run slash command or `Task` subagent without user naming it | “On ‘ready to push’, invoke review-push workflow” |
| `suggest` | Propose capability once; wait for approval | “Offer fix-ci skill when CI fails; don’t run silently” |
| `never-auto` | Only when user names it | “Do not auto-run security auditor on every edit” |

### Example AskQuestion (single bucket)

> **Git / MR:** When you want merge-ready work, what should happen without you naming a tool?
> - Auto-run a specific skill/agent (you’ll name it next)
> - Suggest once, I approve
> - Only when I name the slash/command
> - N/A — I always drive git manually

Follow-up (if auto): free text or pick from Phase A suggestions → one **trigger phrase** + **capability id** (skill path, agent name, or `server.tool`).

## Output shape in `CLAUDE.md` §6

Compact **trigger table** (not prose essay):

```markdown
## Tooling & agents

| When (trigger) | Capability | Mode |
|----------------|------------|------|
| User asks to bump/upgrade deps | skill `…/bump-versions` | load-first |
| “ship it” / “ready to push” | skill or agent `…` | invoke |
| Library/API setup questions | MCP context7 | load-first |
| Large repo exploration (>N files) | Task `explore` | invoke |
| — | security auditor | never-auto |
```

## Synthesis rules

- Cap at ~15 rows; defer rare cases to “ask user.”
- Triggers must be **observable** (phrase, file pattern, task class)—not “when appropriate.”
- Project-only skills belong in **project** `CLAUDE.md` tooling section, not user-global.
- Deduplicate: orchestration ≠ “read CONTRIBUTING first” (that’s **Context before action** in comm).
- User may **waive** §6 on design only with explicit opt-in (“no installed plugins / I drive tools manually”).

## Project scope (design/review)

Shorter pass: repo-local plugins, `AGENTS.md` subagents, CI vendor—after `project-init-flow.md` explore. Align with `agents-md-bridge.md` (parallel instruction files, not vendor-specific paths).
