# Audit: skill — rr-coder/SKILL.md

## Target
- Path: `skills/rr-builder/rr-coder/SKILL.md`
- Type: skill

## Summary
- Verdict: FAIL
- Static: FAIL (path-match only — accepted exception for nested lane skills)
- Top patterns: VAGUE, ORCHESTRATION

## Severity summary
- Critical: 2/3
- Major: 6/6
- Minor: 2/3

## Static checks

| id | Severity | PASS/FAIL | Evidence |
|----|----------|-----------|----------|
| static.name.path-match | critical | FAIL | name='rr-coder' folder='rr-builder' (accepted exception) |
| (all other static) | — | PASS | 11/12 |

## Judgment

| id | Severity | PASS/FAIL | Evidence |
|----|----------|-----------|----------|
| skill.scope.single-outcome | critical | PASS | Purpose: apply production code standards |
| skill.procedure.stop-points | critical | FAIL | **apply** step (L32) lacks observable Done:; load and emit have Done: |
| skill.routing.no-chain-only | critical | PASS | No slash-only execution path |
| skill.discovery.when-clause | major | PASS | description states WHAT + WHEN |
| skill.anti-triggers | major | PASS | When not to use table |
| skill.progressive-disclosure | major | PASS | Required Knowledge names load order |
| skill.consistency | major | PASS | No contradictions |
| skill.refs.no-body-echo | major | PASS | Matrix is intentional lookup, not ref echo |
| skill.refs.unique-contribution | major | PASS | Each ref adds distinct constraints |
| skill.noise.signal-ratio | minor | PASS | No generic encouragement |
| skill.orchestration.todo-mapping | minor | FAIL | Multi-step Procedure without TodoWrite or single-shot N/A line |
| skill.refs.load-efficiency | minor | PASS | No duplicate co-loaded refs |

## Findings (narrative)
- **VAGUE:** apply step missing Done: condition (stop-points).
- **ORCHESTRATION:** No TodoWrite guidance for 3-step Procedure.

## Recommended next step (user)
- FAIL: fix apply Done: and add TodoWrite N/A line
