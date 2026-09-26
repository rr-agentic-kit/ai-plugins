# Inline executor design

Judgment for **parent-only Task executors** under `skills/<name>/refs/executors/<role>.md`. Shared principles: `design/design-core.md`. Catalog agents: `design/agent.md`. Field shape: `templates/executor.template.md` (agent body **without** YAML frontmatter).

## Terminology

| Term | Meaning |
|------|---------|
| **inline executor** | Same as **Task executor** and **inline-agent** (user term) |
| **Location** | `skills/<name>/refs/executors/<role>.md` — no discovery frontmatter |
| **Spawn** | Parent action spawns `generalPurpose` Task + Read executor + Caller Load |

## When to pick

| Need | Pick | SoT |
|------|------|-----|
| Discoverable Task / `@`-mention role (any skill or user may invoke) | Plugin **`agents/`** | `design/agent.md` |
| Parent-only executor (one owning skill; must not ambient-discover) | **`refs/executors/<role>.md`** | This file |
| Parent chat does the work inline (no isolated context) | Parent-inline in action Procedure | `design/skill.md` |
| Reusable orchestrated procedure with own routing/TodoWrite | Internal sub-skill | `design/design-core.md` picker |

Type picker table only: `design/design-core.md` **Shared knowledge layout** — do not duplicate here.

## File layout checklist

| Artifact | Required when |
|----------|---------------|
| `refs/executors/<role>.md` | Always — executor spec |
| `refs/templates/<parent-action>-task.template.md` | Parent spawns Task (or use generic `templates/task-prompt.template.md`) |
| `refs/templates/reports/<kind>.schema.json` + `<kind>.md.j2` | Report output is **SCRIPTABLE** (lean emit) |
| `scripts/render_*.py` | Parent validates lean JSON and renders markdown |

## Body contract

Same sections as `templates/agent.template.md` / `templates/executor.template.md`:

| Section | Required |
|---------|----------|
| Title + owned-by one-liner | Yes — no YAML frontmatter |
| **Role** | Yes — function-style; domain boundary ≤3 sentences |
| **Tools and boundaries** | Yes — portable MUST/MUST NOT body fence |
| **Stop conditions** | Yes — ≥2 concrete triggers (`ok` / `partial` / `failed` or equivalent) |
| **Inputs** | Yes — Caller Load table (required vs stable hard-links vs variant inject) |
| **Outputs** | Yes — link template path; lean emit when applicable |
| **Orchestration** | Optional — single-shot N/A or parallel/merge notes |

**Critical:** No YAML discovery block (`name` / `description`). Static id: `inline-executor.no-frontmatter`.

## Caller Load

Parent Task prompt carries payload fields; executor **Inputs** documents the contract.

| Column | Meaning |
|--------|---------|
| **Required** | Missing → `failed` status + clarification bullets |
| **Stable hard-links** | Executor may Read without re-injection; parent still lists in Task prompt |
| **Variant inject** | Parent must inject (type rubric, method ref) — executor MUST NOT ambient-discover parent pack |

**Lean emit (when parent merges large reports):**

| Field | Purpose |
|-------|---------|
| `emit: lean-json` | Task writes schema-shaped JSON, not full markdown |
| `lean_out` | Absolute scratch path (e.g. `.ai/learning/<run-id>/<kind>.json`) — Write fence: **only** this path when named |

Chat return stays tiny (status + counts + path); parent reads lean JSON or rendered markdown.

## Parent orchestration

| Rule | Do |
|------|----|
| Subagent type | Spawn **`generalPurpose`** (or Claude generic Agent) — not catalog subagent types |
| Parallel work | Multiple Task calls in **one turn**; merge in parent |
| Inject list | Document in owning action Ref index + `skill.orchestration.agent-inject` on orchestrator SKILL |
| Task prompt | Fill `templates/task-prompt.template.md` or action-specific template |
| Nested Task | **Forbidden** from executor |
| Parent re-invoke | Executor MUST NOT invoke owning orchestrator skill for same job |
| Write gates | Executor runs **no** write gates — parent owns static → reflection → pre-ship |

Exemplar parent step: `actions/improve.md` → `improve-2-parallel-audits`.

## Lean emit + render

When report output would bloat context or reinvent table math:

1. Executor emits lean JSON per `refs/templates/reports/<kind>.schema.json`
2. Parent runs `scripts/render_*.py` (CE: `scripts/render_ce_report.py`)
3. Agents **Read** schema only — never `*.md.j2`

SoT: `templates/reports/README.md`, `helper-cli.md` **Lean emit + schema + render**.

## Stop rules

| Rule | Detail |
|------|--------|
| Single-shot | One invocation → one typed result |
| No nested Task | Executor does not spawn subagents |
| No parent skill reinvoke | Parent owns orchestration |
| Write fence | When `lean_out` named: Write **only** that path; no Edit/Write on target skill paths |
| Non-interactive | Clarifications as markdown bullets; no user prompts |
| No template echo | Link output template / schema — do not paste template body into executor file |

## Exemplar map

| Role | Executor | Parent action | Task template | Lean schema |
|------|----------|---------------|---------------|-------------|
| Compliance audit | `refs/executors/compliance.md` | `actions/improve.md` | `templates/improve-compliance-task.template.md` | `templates/reports/compliance.schema.json` |
| Opportunity audit | `refs/executors/opportunity.md` | `actions/improve.md` | `templates/improve-opportunity-task.template.md` | `templates/reports/opportunity.schema.json` |
| Parallel spawn step | — | `actions/improve.md` `improve-2-parallel-audits` | Both templates above | Parent renders via `render_ce_report.py` |

Link exemplars; do not duplicate executor bodies in this ref.

## Critique triggers

| Trigger | Response |
|---------|----------|
| Parent-only role under `agents/` | Move to `refs/executors/<role>.md`; remove catalog frontmatter |
| Missing **Inputs** Caller Load table | Critical — add required / stable / variant columns |
| Missing parent inject documentation | Add to action Ref index; fix `skill.orchestration.agent-inject` on orchestrator |
| Template body pasted into executor | Echo — link template path only |
| Nested Task from executor | Forbidden — parent owns delegation |
| Catalog subagent type in spawn instructions | Use `generalPurpose` + Read executor ref |
| Full markdown in Task return when `lean_out` set | Parent renders; chat return stays tiny |
