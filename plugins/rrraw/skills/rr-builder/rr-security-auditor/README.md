# rr-security-auditor

OWASP-focused security audit for **rr-builder**. Report-only in v1.

## Goals

Audit scoped code for OWASP Top 10, secrets, and language-specific vulnerabilities; emit findings only when confidence gates pass.

## Scope / limits

- Report-only in v1 — no auto-fix (even with `--fix`)
- CPNNN / SRP / test coverage → **rr-coder** / **rr-tester**
- Confidence and Do-not-flag rules authoritative in [refs/confidence.md](refs/confidence.md)

## Audience

Agents loaded by **rr-builder** security routing or **rr-review** security lane.

## When to use

Security review, vulnerability checks, secrets audit, or pre-ship security pass on new/modified code.

## Refs

| Ref | Purpose |
|-----|---------|
| [secure.owasp.md](refs/secure.owasp.md) | OWASP Top 10 patterns |
| [secure.principles.md](refs/secure.principles.md) | Secrets and PII |
| [confidence.md](refs/confidence.md) | Emit gates |
| `*.secure.md` | Language-specific |

Loaded by **rr-review** security lane or direct **rr-builder** security routing.
