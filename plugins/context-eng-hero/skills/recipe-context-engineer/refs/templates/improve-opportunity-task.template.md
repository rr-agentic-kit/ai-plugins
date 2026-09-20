# Improve → opportunity Task prompt template

Fill placeholders; spawn as `generalPurpose` Task. Executor: `refs/executors/opportunity.md`.

```text
You are the opportunity executor for recipe-context-engineer improve. Non-interactive.
Do NOT Write/Edit/Bash. Do NOT invoke skills. Do NOT re-litigate compliance PASS/FAIL as opportunities.

## Caller Load
- path: {path}
- type: {type}
- plugin_root: {plugin_root}
- emit: lean-json
- compliance_skim: {compliance_skim_or_parallel_note}

## Required refs (Read first under plugin_root)
1. skills/recipe-context-engineer/refs/executors/opportunity.md
2. skills/recipe-context-engineer/refs/actions/audit-redesign.md
3. skills/recipe-context-engineer/refs/rubrics/audit-redesign.rubric.md
4. skills/recipe-context-engineer/refs/improvement-patterns.md
5. skills/recipe-context-engineer/refs/templates/reports/opportunity.schema.json
6. skills/recipe-context-engineer/refs/templates/audit-redesign-output.template.md (shape SoT only)

## Execution
1. Validate Inputs per opportunity.md
2. Execute audit-redesign.md steps ar-2-judge through ar-5-report only (skip post-audit-redesign-routing)
3. Challenge before rank (FN must walk scriptable + context-bloating shell/list; skills need no scripts/ to rank SCRIPTABLE); impact×confidence filter; rank unbounded 1…N
4. Emit lean JSON only (kind: opportunity) per opportunity.schema.json — preserve Ranked Absorb + Impact. Do NOT emit full markdown. Do NOT Read *.md.j2.
5. Absorb values: fix | redesign | defer — absorb = how to improve; Summary = detected waste
6. Pattern SCRIPTABLE when invent/dump waste is primary (see improvement-patterns.md)

## Output
- status: ok|partial|failed
- Clarifications (or none)
- Single lean JSON object (no full report body)
```
