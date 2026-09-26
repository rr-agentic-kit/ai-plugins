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

## Philosophy

- **Confidence-gated findings only** — `refs/confidence.md` rules are authoritative; findings below the gate are dropped, not qualified
- **Low-confidence noise is worse than silence** — a quiet report outranks a speculative one
- **Do-not-flag rules win** — patterns excluded by `refs/confidence.md` never appear as findings
- **Report-only** — findings are handed back for the fix lane; the auditor never edits source
- **Language depth on demand** — `*.secure.md` refs load once the stack is identified, not upfront

## Constraints

- Confidence and Do-not-flag rules in `refs/confidence.md` are authoritative
- Language refs (`*.secure.md`) load when stack is identified
- Under **rr-review**, severity-triage + confidence gates both apply
- `disable-model-invocation: true` (no ambient auto-invocation; still callable directly by name)

## Notes

Core refs: `secure.owasp.md`, `secure.principles.md`, `confidence.md`, language `*.secure.md`.
