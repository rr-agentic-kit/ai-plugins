# Frontmatter and naming schemas

**Hard rules** for artifacts in Cursor plugins. Paths are **relative to the plugin root**; no `..`; referenced files must exist before ship.

## Skill (`skills/<name>/SKILL.md`)

| Field / rule | Requirement |
|--------------|-------------|
| Frontmatter | YAML between `---` delimiters |
| `name` | Required; **must equal** parent folder name `<name>` |
| `name` format | `[a-z0-9-]{1,64}` |
| `description` | Required; max **1024** characters (hard); **recommended ≤160** one sentence—shape per invoke mode in `skill-invocation.md` |
| `disable-model-invocation` | Optional boolean—`true` = self-invoke (slash / parent Read); no ambient auto-trigger |
| `user-invocable` | Optional boolean—Claude Code only: `false` hides `/` menu; **not** Cursor schema; never sole control for internals |
| `allowed-tools` | Optional; comma-separated tool names with optional specifiers per Claude Code syntax (e.g. `Bash(python3 scripts/audit_static.py*)`) |
| Path | `skills/<name>/SKILL.md` |

Invoke modes and description rules: `refs/skill-invocation.md`. Sub-skills: `disable-model-invocation: true`; optional `user-invocable: false` on Claude Code.

## Command (`commands/<name>.md`)

| Field / rule | Requirement |
|--------------|-------------|
| Frontmatter | YAML between `---` |
| `name` | Required; **must equal** file stem (`commands/<name>.md`) |
| `description` | Required; **recommended ≤160** one sentence; max 1024 |
| Body | Input contract + delegation to skill **Action** (no internal `refs/` or `plugins/` paths) |

## Rule (`.cursor/rules/*.mdc` or project rules)

| Field / rule | Requirement |
|--------------|-------------|
| Frontmatter | YAML between `---` |
| `description` | Required |
| Targeting | `alwaysApply` and/or `globs` / `path` patterns per product docs; globs must be valid |

## Agent (`agents/<name>.md` or `.cursor/agents/<name>.md`)

| Field / rule | Requirement |
|--------------|-------------|
| Frontmatter | YAML between `---` |
| `name` | Required; consistent with file stem where applicable |
| `description` | Required; **recommended ≤160**; purpose + when; no delegation chains in description |
| Body | Role, tools boundary, **stop conditions** |

## Workflow (markdown doc)

No universal YAML schema; document:

- **Bounded** steps (no infinite loops without exit)
- **Delegation** table (which artifact handles which step)
- **Per-step** output contracts

## All types

- Relative paths only; no `..`
- Internal links in markdown must resolve within the plugin (or external URLs), not dead relative paths
- Do not claim “invoke `/other-command`” as the **only** execution path—commands cannot chain on the platform

## Validity

After authoring, run static → `pre-write-reflection.md` → `pre-ship-checklist.md` (see `refs/actions/shared-write-gates.md`) for **create** / **fix** / **redesign** / **design assist write** before writing files.
