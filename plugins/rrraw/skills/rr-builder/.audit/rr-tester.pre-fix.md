# Audit: skill — rr-tester/SKILL.md

## Target
- Path: `skills/rr-builder/rr-tester/SKILL.md`
- Type: skill

## Summary
- Verdict: FAIL
- Static: FAIL (path-match only — accepted exception for nested lane skills)
- Top patterns: VAGUE, REDUNDANT, ORCHESTRATION

## Severity summary
- Critical: 1/3
- Major: 4/6
- Minor: 1/3

## Static checks

| id | Severity | PASS/FAIL | Evidence |
|----|----------|-----------|----------|
| static.name.path-match | critical | FAIL | name='rr-tester' folder='rr-builder' (accepted exception) |
| (all other static) | — | PASS | 11/12 |

## Judgment

| id | Severity | PASS/FAIL | Evidence |
|----|----------|-----------|----------|
| skill.scope.single-outcome | critical | PASS | Purpose: normalize flags, delegate agents |
| skill.procedure.stop-points | critical | FAIL | **load** (L32) and **route** (L33) lack Done: |
| skill.routing.no-chain-only | critical | PASS | Task delegation, not slash-only |
| skill.discovery.when-clause | major | PASS | description states WHAT + WHEN |
| skill.anti-triggers | major | PASS | When not to use table |
| skill.progressive-disclosure | major | PASS | Shared refs table names ownership |
| skill.consistency | major | FAIL | complete-missing chain: input-resolution L129 `…write,assess` vs SKILL L54 and determinism.md include verify |
| skill.refs.no-body-echo | major | FAIL | Action routing table (L47–66) duplicates input-resolution.md |
| skill.refs.unique-contribution | major | PASS | Shared refs each own distinct domain |
| skill.noise.signal-ratio | minor | PASS | No generic encouragement |
| skill.orchestration.todo-mapping | minor | FAIL | Multi-step Procedure without TodoWrite guidance |
| skill.refs.load-efficiency | minor | FAIL | Routing table is strict subset of input-resolution.md |

## Findings (narrative)
- **VAGUE:** load and route steps missing Done: (stop-points).
- **REDUNDANT:** Action routing table echoes input-resolution.md flag→agent mapping.
- **ORCHESTRATION:** No TodoWrite ids for multi-phase chains.
- **CONSISTENCY:** complete-missing chain missing verify step in input-resolution.md.

## Recommended next step (user)
- FAIL: dedupe routing table, align chain, add Done:/TodoWrite to Procedure
