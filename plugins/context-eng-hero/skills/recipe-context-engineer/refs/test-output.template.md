# Test output template

Behavior report from **Action: test**—no file edits.

```markdown
# Behavior test: <artifact-type> — <file-or-title>

## Target
- Path: `<relative-path>`

## Probes run
List each probe id from `<type>.test-prompts.md` and the exact prompt variant used.

## Results

| Probe | Outcome | Notes |
|-------|---------|-------|
| P1 | PASS / FAIL / AMBIGUOUS | … |
| … | … | … |

## Regression risks
- …

## Suggested follow-ups (user)
- Probe FAIL on **same contract** (wording, stop rule, missing step): `/context-engineer-fix` + this report
- FAIL or user story implies **wrong outcome or capability**: `/context-engineer-redesign`
- PASS with unverified ship: optional `/context-engineer-audit`
```
