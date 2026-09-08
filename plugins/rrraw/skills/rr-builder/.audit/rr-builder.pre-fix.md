# Audit: skill — rr-builder/SKILL.md

## Target
- Path: `skills/rr-builder/SKILL.md`
- Type: skill

## Summary
- Verdict: PASS
- Static: PASS (12/12)
- Top patterns: none

## Severity summary
- Critical: 3/3
- Major: 6/6
- Minor: 3/3

## Static checks

| id | Severity | PASS/FAIL | Evidence |
|----|----------|-----------|----------|
| static.name.path-match | critical | PASS | name='rr-builder' folder='rr-builder' |
| (all other static) | — | PASS | 12/12 |

## Judgment

| id | Severity | PASS/FAIL | Evidence |
|----|----------|-----------|----------|
| skill.scope.single-outcome | critical | PASS | Purpose: classify + Read one nested skill |
| skill.procedure.stop-points | critical | PASS | Steps resolve/classify/execute have Done: |
| skill.routing.no-chain-only | critical | PASS | No slash-only execution path |
| skill.discovery.when-clause | major | PASS | description states WHAT + WHEN (third person) |
| skill.anti-triggers | major | PASS | When not to use table with ≥1 row |
| skill.progressive-disclosure | major | PASS | Shared refs table names load timing |
| skill.consistency | major | PASS | No contradictions across sections |
| skill.refs.no-body-echo | major | PASS | Refs not restated in body |
| skill.refs.unique-contribution | major | PASS | Each ref adds distinct constraints |
| skill.noise.signal-ratio | minor | PASS | No generic encouragement paragraphs |
| skill.orchestration.todo-mapping | minor | PASS | TodoWrite ids resolve/classify/load/execute |
| skill.refs.load-efficiency | minor | PASS | No duplicate co-loaded refs |

## Findings (narrative)
- No judgment failures. Router skill is well-structured.

## Recommended next step (user)
- PASS: ship or run `/context-engineer-test` if behavior unverified
