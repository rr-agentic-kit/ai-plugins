# Improve → compliance Task prompt template

Fill placeholders; spawn as `generalPurpose` Task. Executor: `refs/executors/compliance.md`.

```text
You are the compliance executor for recipe-context-engineer improve. Non-interactive.
Do NOT Write/Edit. Do NOT invoke skills. Do NOT run audit-redesign.

## Caller Load
- path: {path}
- type: {type}
- plugin_root: {plugin_root}
- emit: lean-json

## Required refs (Read first under plugin_root)
1. skills/recipe-context-engineer/refs/executors/compliance.md
2. skills/recipe-context-engineer/refs/actions/audit.md
3. skills/recipe-context-engineer/refs/rubrics/{type_rubric}.rubric.md
4. {skill_ref_rubric_line_or_omit}
5. skills/recipe-context-engineer/refs/templates/reports/compliance.schema.json
6. skills/recipe-context-engineer/refs/templates/audit-output.template.md (shape SoT only)
7. skills/recipe-context-engineer/refs/failure-patterns.md (recommended)

## Execution
1. Validate Inputs per compliance.md
2. Execute audit.md steps audit-2-static through audit-5-report only (skip post-audit-routing)
3. Before static: ◆ Running static audit (~5–10s)…
4. From plugin_root: python3 scripts/audit_static.py . {static_relative_path}
5. Emit lean JSON only (kind: compliance) per compliance.schema.json — every Findings FAIL id in checks[]; severity pass/total as integers. Do NOT emit full markdown. Do NOT Read *.md.j2.

## Output
- status: ok|partial|failed
- Clarifications (or none)
- Single lean JSON object (no full report body)
```

**Placeholders:** `{type_rubric}` = `skill` | `command` | …; for Skill+Ref also inject `rubrics/skill-ref.rubric.md` as item 4; `{static_relative_path}` = file path static accepts (pack entrypoint `…/SKILL.md` when path is a folder).
