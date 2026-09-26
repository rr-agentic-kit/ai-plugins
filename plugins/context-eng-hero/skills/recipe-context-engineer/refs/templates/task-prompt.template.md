# Task prompt template (generic)

Fill placeholders; spawn as `generalPurpose` Task. Executor: `refs/executors/{role}.md`.

For improve-specific copies, see `templates/improve-compliance-task.template.md` and `templates/improve-opportunity-task.template.md` — this file is SoT for **new** orchestrator parents.

```text
You are the {role} executor for {skill_name} {parent_action}. Non-interactive.
{write_fence_line}
Do NOT invoke skills. Do NOT {forbidden_actions}.

## Caller Load
- path: {path}
- type: {type}
- plugin_root: {plugin_root}
{lean_out_line}
{emit_line}
{optional_payload_lines}

## Required refs (Read first under plugin_root)
1. skills/{skill_name}/refs/executors/{role}.md
{required_refs_list}

## Execution
{execution_steps}

## Output (chat — keep tiny)
- status: ok|partial|failed
- Clarifications (or none)
{summary_fields}
- lean_out path written (when applicable)
- Do NOT paste full lean JSON or report markdown into chat when lean_out was written
```

**Placeholders**

| Token | Meaning |
|-------|---------|
| `{role}` | Executor file stem (`compliance`, `opportunity`, …) |
| `{skill_name}` | Owning skill folder name |
| `{parent_action}` | Owning action id (e.g. `improve`) |
| `{write_fence_line}` | e.g. `Write ONLY to Caller Load lean_out when provided.` or `Do NOT Write or Edit.` |
| `{forbidden_actions}` | Role-specific MUST NOTs (Bash, nested Task, parent re-invoke) |
| `{path}` | Plugin-relative target artifact |
| `{type}` | From `classify.md` |
| `{plugin_root}` | Absolute or session cwd plugin root |
| `{lean_out_line}` | `- lean_out: {absolute_scratch_json_path}` when lean emit |
| `{emit_line}` | `- emit: lean-json` when lean emit |
| `{optional_payload_lines}` | Extra Caller Load fields (e.g. `compliance_skim`) |
| `{required_refs_list}` | Numbered injected procedure, rubric, schema, template shape SoT paths |
| `{execution_steps}` | Ordered steps from executor **Execution** or parent action |
| `{summary_fields}` | Tiny chat bullets (verdict, counts) — not full report body |

**Spawn rules:** `generalPurpose` only; parallel independent Tasks in one parent turn when action allows; merge in parent.
