# rr-security-auditor

OWASP-focused security audit lane for **rr-builder**. Report-only.

## Why

Security review must emit findings only when confidence gates pass — low-confidence noise is worse than silence. Done when a scoped report lists HIGH/MEDIUM findings that cleared confidence + Do-not-flag rules.

## What

Audits scoped code for OWASP Top 10, secrets exposure, and language-specific vulnerabilities. Emits report artifacts; does not auto-fix.

**Out of scope:** CPNNN / SRP / observability (**rr-coder**); test verdicts (**rr-tester**); auto-fix (unsupported).

## When

### Use when

- **rr-builder** `--security` handoff (without `--review`)
- Security lane under **rr-review** / builder auto **review**
- Proactive review of new/modified code
- Pre-ship security pass (report-only)

### Avoid when

- CPNNN / SRP / observability on production code → **rr-coder**
- Test verdicts and coverage → **rr-tester**
- Expecting auto-fix of security findings → not supported

## Constraints

- Confidence and Do-not-flag rules in `refs/confidence.md` are authoritative
- Language refs (`*.secure.md`) load when stack is identified
- Under **rr-review**, severity-triage + confidence gates both apply
- `disable-model-invocation: true` / `user-invocable: false`

## Notes

Core refs: `secure.owasp.md`, `secure.principles.md`, `confidence.md`, language `*.secure.md`.
