# Skill invocation frontmatter

Two fields, two sides of the same coin. Use both only when each applies.

| Field | Blocks | Allows |
|-------|--------|--------|
| `disable-model-invocation: true` | Agent auto-trigger from description | User `/skill-name` (and explicit `Read` by agent or parent skill) |
| `user-invocable: false` | Human `/skill-name` (hides from `/` menu on Claude Code) | Agent auto-trigger from description |

## Platform behavior

| Field | Claude Code | Cursor |
|-------|-------------|--------|
| `disable-model-invocation: true` | No auto-trigger; **also drops description from ambient listing** (token savings) | No auto-trigger only; docs do **not** claim ambient-description exclusion |
| `user-invocable: false` | Documented; hides from `/` menu | **Not in frontmatter schema** — likely ignored; treat as Claude-only |

## Three invoke modes

Resolve mode **before** drafting `description` and flags (AskQuestion when unclear—see `questioning.md`).

| Mode | User wants | Flags | Description job |
|------|------------|-------|-----------------|
| **Auto-invoke** | Ambient match on task | neither flag (default) | Listing text **is** sent to the model — write for selection |
| **Self-invoke** | Human `/name` or parent `Read` / Action; not every related prompt | `disable-model-invocation: true` | Schema still requires `description`; Claude drops it from ambient listing; Cursor: no auto-trigger, **do not claim** listing exclusion |
| **Background** | Agent auto-pull; hide from `/` (Claude) | `user-invocable: false` **without** disable | Description **is** the discovery surface — write for auto-pull, not slash UX |

## When to use `disable-model-invocation: true`

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

## When to use `user-invocable: false`

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

## Dual-runtime default (internal / action-like)

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

## Description: optimize for invocation mode

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

## Anti-patterns (binary audit)

| Anti-pattern | Why it fails |
|--------------|--------------|
| `user-invocable: false` as the **only** flag on internal/utility skills | Leaves auto-trigger on in Claude Code; no portable ambient block |
| Assuming Cursor honors `user-invocable: false` | Field absent from Cursor schema; both human and agent may invoke |
| Assuming Cursor saves description tokens like Claude Code | Only `disable-model-invocation` is documented for no auto-trigger in Cursor |
| `disable-model-invocation: true` on background knowledge the agent should auto-pull | Blocks the wrong side; use `user-invocable: false` on Claude Code instead |
| Self-invoke description packed with ambient trigger verbs | Invites wrong auto-selection when flags mis-set |
| Description >160 without justification | Bloat in listing that *does* get sent on auto-invoke paths |

## Agents and sub-skills

Agents are not skills but share description rules (≤160, no delegation chains).

Sub-skills (internal phases): require `disable-model-invocation: true`; optional `user-invocable: false` on Claude Code. Parent agent or workflow owns invocation—sub-skill body does not advertise ambient triggers.
