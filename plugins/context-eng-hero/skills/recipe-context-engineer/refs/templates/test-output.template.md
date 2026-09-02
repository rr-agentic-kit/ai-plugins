# Test output template

Behavior report from **Action: test**—no file edits.

**AMBIGUOUS** does not count as PASS (see `actions/test.md`).

```markdown
# Behavior test: <artifact-type> — <file-or-title>

## Target
- Path: `<relative-path>`

## Probes run
List each probe id from `prompts/<type>.prompt.md` and the exact prompt variant used.

## Results

| Probe | Outcome | Notes |
|-------|---------|-------|
| P1 | PASS / FAIL / AMBIGUOUS | … |
| … | … | … |

## Regression risks
- …

## Suggested follow-ups (user)
- Probe FAIL on **same contract** (wording, stop rule, missing step): fix using probe ids from this report
- FAIL or user story implies **wrong outcome or capability**: redesign
- PASS with unverified ship: optional audit
- AMBIGUOUS only: re-run probe or ask once—do not thicken artifact from AMBIGUOUS alone
```
