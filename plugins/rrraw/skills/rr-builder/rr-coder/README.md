# rr-coder

Production code standards for **rr-builder**. Language-specific refs live under `refs/`.

## Goals

Apply SOLID, CPNNN rubric, architecture, and observability standards to production/application source — implement, refactor, or code-lane review with CP findings and mandatory **`## Architecture`** section.

## Scope / limits

- Application source only — dedicated test paths excluded from production findings
- Test strategy and gaps → **rr-tester**; OWASP → **rr-security-auditor**
- Language tutorial refs load on demand; not rewritten here

## Audience

Agents loaded by **rr-builder** or **rr-review** code lane. **rr-tester** also loads this skill so test code matches implementation rules.

## When to use

Implement/refactor production code or run code-lane review under **rr-review**.

## Load matrix

See [SKILL.md](SKILL.md) — universal principles first, then language detection from extensions and build files.

## Review output

Code lane reports include:

1. CP finding table (per [compliance-rubric.md](refs/compliance-rubric.md))
2. Mandatory **`## Architecture`** section (per [architecture.md](refs/architecture.md))
3. Challenge appendix when run under **rr-review** ([severity-triage.md](refs/severity-triage.md))

## Related

| Topic | Path |
|-------|------|
| Test code style | **rr-tester** loads this skill |
| Security audit | **rr-security-auditor** |
| Multi-lane review | **rr-review** |
