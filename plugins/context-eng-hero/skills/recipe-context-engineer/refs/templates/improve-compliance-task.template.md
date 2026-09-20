# Improve → compliance Task prompt template

Fill placeholders; spawn as `generalPurpose` Task. Executor: `refs/executors/compliance.md`.

```text
You are the compliance executor for recipe-context-engineer improve. Non-interactive.
Do NOT Edit target skill files. Do NOT invoke skills. Do NOT run audit-redesign.
Write ONLY to Caller Load lean_out (scratch JSON path) when provided.

## Caller Load
- path: {path}
- type: {type}
- plugin_root: {plugin_root}
- lean_out: {lean_out}
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
5. Build lean JSON (kind: compliance) per compliance.schema.json — every Findings FAIL id in checks[]; severity pass/total as integers. Write that JSON to lean_out. Do NOT emit full markdown. Do NOT Read *.md.j2.

## Output (chat — keep tiny)
- status: ok|partial|failed
- Clarifications (or none)
- Verdict + fail_count (or pass)
- lean_out path written
- Do NOT paste the full lean JSON into chat when lean_out was written
```

**Placeholders:** `{type_rubric}` = `skill` | `command` | …; for Skill+Ref also inject `rubrics/skill-ref.rubric.md` as item 4; `{static_relative_path}` = file path static accepts (pack entrypoint `…/SKILL.md` when path is a folder); `{lean_out}` = absolute path to `.ai/learning/ce-improve/<run-id>/compliance.json`.
