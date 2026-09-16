# Design core (shared principles)

Shared judgment for **skills**, **commands**, and **agents**. Type-specific files: `design/skill.md`, `design/command.md`, `design/agent.md`. Field tables: `frontmatter-schemas.md` (mechanical SoT). Do not restate schema tables here.

Read at draft/plan steps with `design/<type>.md` + `frontmatter-schemas.md`. One hop: type files do **not** chain to each other.

## Signal vs noise

- **Signal**: constraints the agent cannot infer (policy, gates, exact formats, stop rules).
- **Noise**: generic encouragement, repeated restatements, prose that duplicates co-loaded refs.

Cut noise until every paragraph changes behavior or discovery. If parent SKILL / action Ref index co-loads file X with this ref, do not restate X's constraints here.

## Forcing function

When a choice is enumerable, prefer **AskQuestion** over open-ended asks. Always pair with the **mandatory text-mode fallback** in `questioning.md` **Delivery channels** so authored clarify/close paths survive harnesses that omit the tool.

**MUST (create/maintain):** Whenever an authored skill, command, or workflow uses AskQuestion or enumerable gates in Procedure / Orchestration / close, the artifact **must** state the Delivery channels rule (prefer AskQuestion when tool present; same options as prose when missing; do not stall). If there are no such gates, one-line N/A (“no AskQuestion gates”) so audit can PASS.

When work spans verifiable steps: action commands → **TodoWrite** with ids from `refs/actions/<verb>.md`; workflows → `todo_id` per step. Design-only skill invoke → no forced todo list unless user chose an action.

## Layer separation

| Layer | Holds |
|-------|--------|
| **Skill** | Judgment, classification, reusable procedure, progressive disclosure |
| **Skill+Ref** | Invariant procedure in SKILL; variant/detail in `refs/`—one hop |
| **Ref file** | Skill-private constraints for one subtask; loaded via parent SKILL / action Ref index |
| **Command** | Slash contract: inputs, delegation to skill **Action**, output shape |
| **Agent** | Isolated-role executor: Role / Tools and boundaries / Stop / Inputs / Outputs |
| **Refs (orchestrator)** | Templates, rubrics, checklists—Read at the step that branches |

Link the canonical ref once; do not duplicate policy in three places.

## Degrees of freedom

| Freedom | When | Shape |
|---------|------|-------|
| **Low** | Fragile, irreversible, safety-critical | Exact steps, stop rules, scripts |
| **Medium** | Repeatable workflow with known forks | AskQuestion, bounded retries |
| **High** | Review, design, classification | Outcomes + anti-patterns + examples |

Default **high** for judgment skills; **low** only where mistakes are costly.

## Progressive disclosure (one level deep)

SKILL.md (or command body) → `refs/` (and `scripts/` **executed**, not pasted). Refs do **not** chain to other refs.

See `helper-cli.md` when the skill folder includes `scripts/`.

## Type picker

| Need | Pick |
|------|------|
| Judgment + progressive disclosure | Skill (+ refs) — `design/skill.md` |
| User slash; no `refs/` leak | Command → skill Action — `design/command.md` |
| Isolated fences + typed I/O + hard stops | Agent — `design/agent.md` |
| Multi-step owners | Workflow (not this pack; use workflow template/rubric) |
| Always-on / situational memory packs | `recipe-static-memory` — not plugin agents |

Do not merge types. A folder with SKILL.md + `refs/` is **Skill+Ref**, not plain **Skill**.

## Access economy (portable first)

Marketplace plugins = **dual-runtime parity** (Cursor + Claude Code).

1. Emit the **portable minimum** always (`name` + `description` + body contracts).
2. Add runtime-specific frontmatter **only** when the authoring target needs it **and** the field is **honored** in that context.
3. Never invent security via fields the runtime ignores (see agent plugin caveats in `design/agent.md` / `frontmatter-schemas.md`).
4. Body tool fences and stop rules are portable; frontmatter tool lists are not dual-runtime SoT.

Field tables: `frontmatter-schemas.md` (**Portable | Cursor | Claude**). Judgment for when to set: `design/<type>.md`.

## Not artifact frontmatter

Do **not** author these as skill/command/agent YAML:

- Workspace / session permission allowlists (`permissions.json`, Claude settings allowlists)
- Auto-review classifiers, managed admin disables
- Claiming Cursor plugin agents honor full Claude `tools` / `permissionMode` surface without evidence

Point once here; teach artifact fields only in schemas + type design files.
