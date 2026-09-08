---
name: rr-security-auditor
description: OWASP security audit with confidence gating. Use for security review, vulnerability checks, or secrets audit; loaded by rr-builder or rr-review security lane. Report-only in v1.
disable-model-invocation: true
user-invocable: false
---

# rr-security-auditor

**Human overview:** [README.md](README.md)

## Purpose

Audit scoped code for OWASP Top 10, secrets exposure, and language-specific vulnerabilities. Emit findings only when [refs/confidence.md](refs/confidence.md) gates pass. Report-only in v1 — no auto-fix.

## When to use

- Security lane under **rr-review**
- Proactive review of new/modified code
- Pre-ship security pass (report-only)

## When not to use

| Need | Use instead |
|------|-------------|
| CPNNN / SRP / observability on production code | **rr-coder** |
| Test verdicts and coverage | **rr-tester** |
| Auto-fix security findings | Not supported in v1 |

## Procedure

Fixed 3-step audit flow: TodoWrite N/A.

1. **load** — Read [secure.owasp.md](refs/secure.owasp.md), [secure.principles.md](refs/secure.principles.md), [confidence.md](refs/confidence.md); add language ref when stack is identified (table below). Done: confidence rules loaded before any finding.
2. **trace** — Classify each observation per confidence.md; drop LOW and Do-not-flag patterns. Done: only HIGH/MEDIUM candidates remain.
3. **emit** — When loaded by **rr-review**, apply [severity-triage.md](refs/severity-triage.md) + confidence gates. Format report per **Output format** below. Done: report-only (even with `--fix`).

**Language-specific:**

| Extension | Ref |
|-----------|-----|
| `.java` | [java.secure.md](refs/java.secure.md) |
| `.kt` | [kotlin.secure.md](refs/kotlin.secure.md) |
| `.ts` / `.tsx` | [typescript.secure.md](refs/typescript.secure.md) |
| React `.tsx` | also [react.secure.md](refs/react.secure.md) |
| `.py` | [python.secure.md](refs/python.secure.md) |

No matching language ref → OWASP + principles + confidence only; note `Language ref: none (OWASP-only)` in report header.

## Output format

```markdown
## Security Audit: [scope]

**Environment**: Development | Production
**Status**: ✅ Pass | ⚠️ Warnings | ❌ Blocked

### Critical Issues (blocks commit)
| Location | Issue | OWASP | Confidence | Fix |

### High Issues (should fix)
| Location | Issue | OWASP | Confidence |

### Needs Verification (MEDIUM confidence)
| Location | Issue | Question |

### Passed Checks
- ✅ …
```

Confidence levels, emit gates, and Do-not-flag rules: [refs/confidence.md](refs/confidence.md).
