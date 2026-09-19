# Frontmatter and naming schemas

**Hard rules** for artifacts in Cursor + Claude marketplace plugins. Paths are **relative to the plugin root**; no `..`; referenced files must exist before ship.

**SoT split:** this file = mechanical field tables. Judgment (“when to set”) = `design/<type>.md`. Shared access economy = `design/design-core.md`.

Columns: **Field | Required | Portable | Cursor | Claude | Notes**.

## Skill (`skills/<name>/SKILL.md`)

| Field | Required | Portable | Cursor | Claude | Notes |
|-------|----------|----------|--------|--------|-------|
| Frontmatter (`---` YAML) | yes | yes | yes | yes | Must parse |
| `name` | yes | yes | yes | yes | **Must equal** parent folder `<name>`; `[a-z0-9-]{1,64}` |
| `description` | yes | yes | yes | yes | Max **1024**; **recommended ≤160**; shape per invoke mode in `design/skill.md` |
| `disable-model-invocation` | no | yes | yes | yes | `true` = self-invoke (slash / parent Read); no ambient auto-trigger |
| `user-invocable` | no | partial | **ignored** | yes | Claude: `false` hides `/` menu; never sole control for internals |
| `allowed-tools` | no | no | no | yes | Turn-scoped **permission grant**, not a hard exclusive allowlist |
| `argument-hint` / `arguments` | no | no | no | yes | When slash-invoked with args |
| `license` | no | yes | optional | optional | agentskills.io optional |
| `compatibility` | no | yes | optional | optional | agentskills.io optional |
| `metadata` | no | yes | optional | optional | agentskills.io optional |
| Path | yes | yes | yes | yes | `skills/<name>/SKILL.md` |

Invoke modes and description rules: `design/skill.md`. Sub-skills: `disable-model-invocation: true`; optional `user-invocable: false` on Claude Code.

## Command (`commands/<name>.md`)

| Field | Required | Portable | Cursor | Claude | Notes |
|-------|----------|----------|--------|--------|-------|
| Frontmatter (`---` YAML) | yes | yes | yes | yes | Must parse |
| `name` | yes | yes | yes | yes | **Must equal** file stem |
| `description` | yes | yes | yes | yes | **Recommended ≤160**; max 1024 |
| `argument-hint` | no | no | no | yes | When slash expects args |
| `allowed-tools` | no | no | no | yes | Side-effect narrowing / pre-approve only |
| `model` | no | no | no | yes | Optional pin; prefer omit in marketplace defaults |
| Body | yes | yes | yes | yes | Input + Action delegation + output; no internal `refs/` / `plugins/` paths |

Judgment: `design/command.md`.

## Agent (`agents/<name>.md` or `agents/<group>/<name>.md`)

| Field | Required | Portable | Cursor | Claude | Notes |
|-------|----------|----------|--------|--------|-------|
| Frontmatter (`---` YAML) | yes | yes | yes | yes | Must parse |
| `name` | yes | yes | yes | yes | **Must equal** file stem (nested OK: `agents/planning/challenge.md` → `name: challenge`) |
| `description` | yes | yes | yes | yes | **Recommended ≤160**; purpose + when; no delegation chains |
| `model` | no | no | yes | yes | Cursor: `inherit` \| id; Claude: model id; avoid fragile pins in marketplace |
| `readonly` | no | no | yes | no | Cursor judgment-only agents |
| `is_background` / `background` | no | no | `is_background` | `background` | Runtime-specific naming |
| `tools` | no | no | no | yes | Align with **body** fence; not dual-runtime SoT |
| `disallowedTools` | no | no | no | yes | Align with body fence |
| `maxTurns` | no | no | no | yes | When unbounded loops are a risk |
| `skills` (preload) | no | no | no | yes | Optional Claude preload |
| `isolation` / `effort` | no | no | no | yes | Optional Claude |
| ~~`permissionMode`~~ | — | — | — | **ignored in plugins** | Project/user agents only; do not ship as marketplace security |
| ~~`hooks`~~ | — | — | — | **ignored in plugins** | Same caveat |
| ~~`mcpServers`~~ | — | — | — | **ignored in plugins** | Same caveat |
| Body tool fence | yes | yes | yes | yes | **Tools and boundaries** with MUST/MUST NOT — always required |

Judgment: `design/agent.md`. Forbidden: `agents/<id>/refs/`.

## Rule (`.cursor/rules/*.mdc` or project rules)

| Field / rule | Requirement |
|--------------|-------------|
| Frontmatter | YAML between `---` |
| `description` | Required |
| Targeting | `alwaysApply` and/or `globs` / `path` patterns per product docs; globs must be valid |

## Workflow (markdown doc)

No universal YAML schema; document:

- **Bounded** steps (no infinite loops without exit)
- **Delegation** table (which artifact handles which step)
- **Per-step** output contracts

## Ref file (`skills/<name>/refs/**/*.md`)

Skill-private docs — **not** entry points. YAML frontmatter and `description` are **not** required (optional if present). No required `## Purpose` / `## Load` / `## Content` headings; body holds constraints loaded via parent SKILL routing.

| Field / rule | Requirement |
|--------------|-------------|
| Frontmatter | Optional; if present, must be valid YAML between `---` |
| `description` | Not required |
| Body | Title + unique constraints; optional one-line owned-by / load-via prose (see `templates/ref-file.template.md`) |
| Path | `skills/<name>/refs/` or `skills/<name>/references/` (any depth) |

## All types

- Relative paths only; no `..`
- Internal links in markdown must resolve within the plugin (or external URLs), not dead relative paths
- Do not claim “invoke `/other-command`” as the **only** execution path—commands cannot chain on the platform

## Validity

After authoring, run static → `pre-write-reflection.md` → `pre-ship-checklist.md` (see `refs/actions/shared-write-gates.md`) for **create** / **fix** / **redesign** / **design assist write** before writing files.
