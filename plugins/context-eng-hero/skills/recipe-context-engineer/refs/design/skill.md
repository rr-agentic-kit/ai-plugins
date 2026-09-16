# Skill design

Judgment for **Skill** and **Skill+Ref**. Shared principles: `design/design-core.md`. Field tables: `frontmatter-schemas.md`. Helper scripts: `helper-cli.md`. Sibling README: `readme-spec.md`.

## Skill vs Skill+Ref vs Ref

| Shape | When |
|-------|------|
| **Skill** | Single `SKILL.md`; no sibling `refs/` pack |
| **Skill+Ref** | Invariant procedure in SKILL; variant/detail in `refs/`—one hop from progressive disclosure / Action Ref index |
| **Ref file** | Skill-private constraints for one subtask; not an entry point; YAML/`description` optional |

Do not put invariant classify/orchestration that belongs in the parent SKILL into a ref.

## Access economy (skills)

1. Resolve **invoke mode** (Auto / Self / Background) **before** drafting `description` and flags.
2. Add Claude `allowed-tools` only when turn-scoped grants are needed (e.g. `Bash(python3 scripts/…*)`).
3. Never treat `allowed-tools` as “these are the only tools the model may use”—it is a **permission grant**, not a hard allowlist.
4. Optional agentskills metadata (`license`, `compatibility`, `metadata`) only when shipping public skill packs that need them.

## Invoke modes

Two fields, two sides of the same coin. Use both only when each applies.

| Field | Blocks | Allows |
|-------|--------|--------|
| `disable-model-invocation: true` | Agent auto-trigger from description | User `/skill-name` (and explicit `Read` by agent or parent skill) |
| `user-invocable: false` | Human `/skill-name` (hides from `/` menu on Claude Code) | Agent auto-trigger from description |

### Platform behavior

| Field | Claude Code | Cursor |
|-------|-------------|--------|
| `disable-model-invocation: true` | No auto-trigger; **also drops description from ambient listing** (token savings) | No auto-trigger only; docs do **not** claim ambient-description exclusion |
| `user-invocable: false` | Documented; hides from `/` menu | **Not in frontmatter schema** — likely ignored; treat as Claude-only |

### Three modes

Resolve mode **before** drafting `description` and flags (AskQuestion when unclear—see `questioning.md`).

| Mode | User wants | Flags | Description job |
|------|------------|-------|-----------------|
| **Auto-invoke** | Ambient match on task | neither flag (default) | Listing text **is** sent to the model — write for selection |
| **Self-invoke** | Human `/name` or parent `Read` / Action; not every related prompt | `disable-model-invocation: true` | Schema still requires `description`; Claude drops it from ambient listing; Cursor: no auto-trigger, **do not claim** listing exclusion |
| **Background** | Agent auto-pull; hide from `/` (Claude) | `user-invocable: false` **without** disable | Description **is** the discovery surface — write for auto-pull, not slash UX |

### When to use `disable-model-invocation: true`

Portable default for internals. Use when the skill should **not** compete on ambient relevance:

- Side-effectful / destructive (deploy, release, delete-branch, send-message)
- Expensive / slow (full suites, deep audits, retrospectives)
- Internal / utility building blocks invoked by humans or parent skills, not by every related prompt
- Action-like procedures (audit, fix, create) exposed via slash commands

```yaml
---
name: my-internal-skill
description: Outcome-first one sentence for slash or parent Read.
disable-model-invocation: true
---
```

### When to use `user-invocable: false`

**Claude Code extra only.** Not a context-savings lever and not reliable in Cursor.

Use **in addition** to `disable-model-invocation: true` when the skill should also be hidden from the `/` menu (e.g. sub-skills). Never use it alone for internals.

Appropriate Claude-only cases:

- Background knowledge the agent should still auto-pull (e.g. legacy-system-context)
- Cleaning the `/` menu without blocking agent auto-invoke

```yaml
---
name: legacy-system-context
description: Background context for …
user-invocable: false
---
```

### Dual-runtime default (internal / action-like)

For skills meant to be invoked by humans **or** by other skills, **not** by ambient relevance:

- **Required:** `disable-model-invocation: true` — only reliable cross-platform control
- **Optional (Claude Code):** `user-invocable: false` — hide from `/` when also blocking ambient trigger

```yaml
---
name: assess-phase
description: Runs assess stage for review workflow.
disable-model-invocation: true
user-invocable: false   # Claude Code: hide from / menu
---
```

## Description craft

| Bound | Value | Recipe check |
|-------|-------|--------------|
| **Hard max** | 1024 characters | static `static.description.max-length` |
| **Recommended** | ≤160 characters, one sentence | judgment `*.description.recommended-length` + static minor `static.description.recommended-length` |

Write **after** invoke mode is known; count characters before gates.

| Mode | Description shape |
|------|-------------------|
| **Auto-invoke** | Third-person WHAT + WHEN; **trigger keywords** the user would say; no agent IDs / delegation chains; one sentence ≤160 |
| **Self-invoke** | Outcome-first; **no** ambient trigger verbs (audit/fix/redesign/test)—those belong on slash commands; shortest valid sentence ≤160 |
| **Background** | Trigger keywords only (when agent should load this); one sentence ≤160; no slash-menu marketing |
| **Commands** | Outcome-first ≤160 |
| **Agents** | Purpose + when; no delegation chains in description; ≤160 |

Audit **FAIL** if >160 unless user explicitly accepts over-budget (still **FAIL** if >1024).

## Body budget

- Prefer ≤~200 lines in SKILL body; push variant detail into `refs/` (one hop).
- Progressive disclosure / Shared refs / Ref index names which ref for which step.
- Scripts: agent **runs** helpers via shell—do not paste script source (`helper-cli.md`).

## When to set `allowed-tools`

Add only for Claude turn grants that unblock expected side effects (e.g. static audit script). Omit on Cursor-only targets. Align with `frontmatter-schemas.md` Notes—not a substitute for Procedure tool guidance.

## Anti-patterns (binary audit)

| Anti-pattern | Why it fails |
|--------------|--------------|
| `user-invocable: false` as the **only** flag on internal/utility skills | Leaves auto-trigger on in Claude Code; no portable ambient block |
| Assuming Cursor honors `user-invocable: false` | Field absent from Cursor schema; both human and agent may invoke |
| Assuming Cursor saves description tokens like Claude Code | Only `disable-model-invocation` is documented for no auto-trigger in Cursor |
| `disable-model-invocation: true` on background knowledge the agent should auto-pull | Blocks the wrong side; use `user-invocable: false` on Claude Code instead |
| Self-invoke description packed with ambient trigger verbs | Invites wrong auto-selection when flags mis-set |
| Description >160 without justification | Bloat in listing that *does* get sent on auto-invoke paths |
| Treating `allowed-tools` as a hard exclusive allowlist | Mis-teaches Claude semantics; body still needs tool/stop guidance |

## Sub-skills

Require `disable-model-invocation: true`; optional `user-invocable: false` on Claude Code. Parent agent or workflow owns invocation—sub-skill body does not advertise ambient triggers.
