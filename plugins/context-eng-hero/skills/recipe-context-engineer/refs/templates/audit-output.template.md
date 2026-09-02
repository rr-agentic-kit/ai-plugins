# Audit output template

Fill static rows from `scripts/audit_static.py`. Evaluate **Judgment** rows from the type rubric only (skip ids listed under **Static**). **No** numeric score; **no** fixed check count.

```markdown
# Audit: <artifact-type> — <file-or-title>

## Target
- Path: `<relative-path>`
- Type: skill | Skill+Ref | ref file | command | agent | rule | workflow

## Summary
- Verdict: PASS | FAIL
- Static: PASS | FAIL | SKIPPED (<reason if skipped>)
- Top patterns: <from failure-patterns.md>

## Severity summary
- Critical: {pass}/{total}
- Major: {pass}/{total}
- Minor: {pass}/{total}

## Findings (narrative)
- …

## Recommended next step (user)
- PASS: ship or run behavior test if unverified
- FAIL: fix every FAIL in this report
```

**Verdict:** **PASS** only if **all** static and judgment checks pass. STATIC SKIPPED → verdict **FAIL** unless audit-only with no ship intent. Any judgment FAIL → verdict **FAIL**.
