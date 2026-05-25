# Audit output template

Fill static rows from `scripts/audit_static.py`. Evaluate **Judgment** rows from the type rubric only (skip ids listed under **Static**). **No** numeric score; **no** fixed check count.

```markdown
# Audit: <artifact-type> — <file-or-title>

## Target
- Path: `<relative-path>`
- Type: skill | command | agent | rule | workflow

## Summary
- Verdict: PASS | FAIL
- Static: PASS | FAIL | SKIPPED (<reason if skipped>)
- Top patterns: <from failure-patterns.md>

## Severity summary
- Critical: {pass}/{total}
- Major: {pass}/{total}
- Minor: {pass}/{total}

## Static checks
| id | Severity | PASS/FAIL | Evidence |

## Judgment checks (LLM)
| id | Severity | PASS/FAIL | Evidence |

## Findings (narrative)
- …

## Recommended next step (user)
- PASS: ship or run `/context-engineer-test` if behavior unverified
- FAIL: `/context-engineer-fix <path>` with this report; fix must address **every** FAIL
```

**Verdict:** **PASS** only if **all** static and judgment checks pass. Any FAIL → verdict **FAIL**.
