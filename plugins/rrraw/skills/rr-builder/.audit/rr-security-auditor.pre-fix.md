# Audit: skill — rr-security-auditor/SKILL.md

## Target
- Path: `skills/rr-builder/rr-security-auditor/SKILL.md`
- Type: skill

## Summary
- Verdict: FAIL
- Static: FAIL (path-match only — accepted exception for nested lane skills)
- Top patterns: ORCHESTRATION, REDUNDANT

## Severity summary
- Critical: 3/3
- Major: 6/6
- Minor: 2/3

## Static checks

| id | Severity | PASS/FAIL | Evidence |
|----|----------|-----------|----------|
| static.name.path-match | critical | FAIL | name='rr-security-auditor' folder='rr-builder' (accepted exception) |
| (all other static) | — | PASS | 11/12 |

## Judgment

| id | Severity | PASS/FAIL | Evidence |
|----|----------|-----------|----------|
| skill.scope.single-outcome | critical | PASS | Purpose: OWASP audit, report-only |
| skill.procedure.stop-points | critical | PASS | All steps have Done: |
| skill.routing.no-chain-only | critical | PASS | No slash-only execution path |
| skill.discovery.when-clause | major | PASS | description states WHAT + WHEN |
| skill.anti-triggers | major | PASS | When not to use table |
| skill.progressive-disclosure | major | PASS | Language table + confidence ref |
| skill.consistency | major | PASS | No contradictions |
| skill.refs.no-body-echo | major | PASS | Output format is skill-owned contract |
| skill.refs.unique-contribution | major | PASS | Each ref adds distinct constraints |
| skill.noise.signal-ratio | minor | PASS | No generic encouragement |
| skill.orchestration.todo-mapping | minor | FAIL | Fixed 3-step Procedure without TodoWrite or N/A line |
| skill.refs.load-efficiency | minor | PASS | L36 duplicates load step confidence cite (minor dedup) |

## Findings (narrative)
- **ORCHESTRATION:** No TodoWrite N/A for fixed 3-step audit flow.
- **REDUNDANT:** L36 "Follow confidence.md…" duplicates load step L32.

## Recommended next step (user)
- FAIL: add TodoWrite N/A line; remove duplicate confidence line
