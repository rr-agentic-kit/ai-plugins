# Agent design

Judgment for **plugin agents** (`plugins/<plugin>/agents/**/*.md`). Shared principles: `design/design-core.md`. Field tables: `frontmatter-schemas.md`.

## In scope vs out of scope

| In scope | Out of scope (other owner) |
|----------|----------------------------|
| Plugin Task / subagent definitions under `agents/` | `AGENTS.md` / `.agents/{group}.md` → `recipe-static-memory` |
| Nested `agents/<group>/<name>.md` (`name` = file stem) | Parent chat skill invoke → `design/skill.md` |
| Function-style defaults; lighter conversational variant | Slash → skill Action → `design/command.md` |
| | Cross-artifact multi-step → Workflow |
| | `agents/<id>/refs/` — **forbidden** |

## Primary shape: function-style Task executor

Default for marketplace agents (rrraw-like):

| Default | Meaning |
|---------|---------|
| Non-interactive | MUST NOT prompt the user; return clarifications / status instead |
| Caller Load | Parent skill/Task injects refs and payload; agent does not own ambient discovery |
| Write fence | Body states what may be written vs read-only |
| Status stops | Concrete stop triggers (`ok` / `partial` / `failed` or equivalent) |
| Single-shot | One invocation → one typed result; no unbounded “continue until perfect” |
| Handoff economy | Prefer markdown report SoT; full narrative when the output template requires it—no parallel JSON that only restates that report |

**Conversational variant:** lighter Role + Tools + Stop for chatty helpers. Same portable body fence requirement; do not ship dual equal templates—start from function-style and strip only what the product needs.

## Caller Load (operational)

Shared layout SoT: `design/design-core.md` **Shared knowledge layout**.

| Rule | Do |
|------|----|
| Knowledge home | Prefer skill/plugin `refs/` over duplicating judgment in the agent body |
| Stable refs | List hard-link paths under **Inputs**; parent may still inject the same paths in the Task prompt |
| Variant refs | Require parent inject (type rubric, method ref)—agent MUST NOT ambient-discover the parent skill pack |
| **Outputs** | **Link** the output template path; do not paste template sections into the agent |
| Schema echo | Do not invent a parallel JSON handoff when the template is already markdown-table shaped (Ranked / Findings) |
| Orchestrator | MUST NOT instruct invoking the parent orchestrator skill for the same job |

## Access economy (agents) — hardness rule

**Calling a Task ≠ shipping under `agents/`.** File under plugin `agents/**/*.md` registers a **catalog** subagent (`name` + `description` → Cursor Task types / Claude `@`-mention every session). Parent-only executors under skill `refs/executors/` are **not** catalog agents — implementation SoT: `design/inline-executor.md`.

1. **Body tool fence is always required** (portable) — **Tools and boundaries** with MUST / MUST NOT. Frontmatter `tools` / `disallowedTools` are **not** dual-runtime SoT.
2. Marketplace default frontmatter: `name` + `description` only, unless author opts into a runtime. (**Catalog agents only** — parent-only executors under `refs/executors/` have **no** discovery frontmatter.)
3. **Cursor extras when useful:** `readonly: true` for judgment-only agents; `model: inherit` only if teaching/explicit; avoid pinning fragile model IDs in marketplace plugins unless product requires it. Optional `is_background` when Cursor subagent docs apply.
4. **Claude extras when useful and not plugin-ignored:** `tools` / `disallowedTools` aligned with body fence; `maxTurns` when unbounded loops are a risk; optional `skills` preload, `background`, `isolation`, `effort` when honored. **Omit** `permissionMode` / `hooks` / `mcpServers` in **plugin-shipped** agents—they are **ignored** when loaded from a plugin (false security if set).
5. Never confuse workspace `permissions.json` / Claude settings allowlists with artifact frontmatter (`design/design-core.md` **Not artifact frontmatter**).

### Frontmatter decision tree

```
Need only portable marketplace agent?
  → name + description + body fence (Role / Tools / Stop / Inputs / Outputs)
Need Cursor judgment-only?
  → + readonly: true (± model: inherit)
Need Claude tool narrowing / turn bound?
  → + tools/disallowedTools aligned to body; + maxTurns if loop risk
Shipping via plugin?
  → do NOT set permissionMode / hooks / mcpServers (ignored)
Parent-only Task executor (one skill caller)?
  → do NOT put under agents/; use refs/executors/<role>.md (no name/description FM)
```

## Body vs frontmatter tool fence

| Layer | Role |
|-------|------|
| **Body (required)** | Allowlist or denylist with MUST/MUST NOT; portable across runtimes |
| **Frontmatter tools** | Optional Claude (or Cursor) hint—must not contradict body; never sole fence |

**FAIL pattern:** tools claimed only in frontmatter with empty/vague **Tools and boundaries**.

## Description

Purpose + when; ≤160 recommended; no delegation chains or internal agent IDs in `description`.

## Critique triggers

Call out before writing:

| Trigger | Response |
|---------|----------|
| “Put it in `agents/` so Task can call it” (only one parent skill calls it) | Wrong lever — use `refs/executors/<role>.md` + Task Caller Load; `agents/` is discovery registration, not a Task prerequisite |
| Parent-only executor under `agents/` | Stop — catalog tax + ambient invoke; move to owning skill `refs/executors/` (short role names OK there) |
| Bare global noun as catalog `name` (`compliance`, `opportunity`) | Collision risk in `agents/` only — parent-only stays under skill `refs/executors/`, not catalog |
| No body tool fence | Critical gap — add MUST/MUST NOT before gates |
| `permissionMode` / `hooks` / `mcpServers` on plugin agent | False security — remove; document ignored-in-plugins |
| Frontmatter tools without body fence | Align body; FM is not SoT |
| Unbounded “continue until done” | Add stop conditions + optional `maxTurns` |
| Conversational defaults for Task executor role | Prefer function-style; justify variant |
| Nested path but `name` ≠ stem | Static `static.name.path-match` FAIL |
| Agent embeds full rubric/template copy | Echo — link skill/plugin refs; Caller Load |
| Agent invokes parent skill for same job | Forbidden — parent owns orchestration |
| `agents/*/refs/` tree or claim | Forbidden — see design-core picker |
| Mega-role modes holding all skill knowledge | Forbidden — function-style + Caller Load |
| JSON handoff that only restates md Ranked/Findings | Prefer md report SoT; drop parallel schema |
