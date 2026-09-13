# rr-coder

Production code standards lane for **rr-builder** — SOLID, CPNNN, architecture, observability, language refs.

## Why

Implementation and code-lane review need one place for production principles so findings map to stable **CPNNN** IDs and a mandatory architecture section. Done when scoped source matches loaded refs or the CP + Architecture report is emitted.

## What

Applies principles to **application source** only (implement, refactor, or code-lane assess). Language tutorial refs load on demand from extensions and build files.

**Out of scope:** test strategy/gaps (**rr-tester**); OWASP depth (**rr-security-auditor**); MR inline POST (**rr-ci**).

## When

### Use when

- Implement or refactor production/application source via **rr-builder** or **rr-review** code lane
- Code-lane review needing CP findings and mandatory `## Architecture`

### Avoid when

- Test gaps / MISSING verdicts → **rr-tester**
- OWASP / exploitability → **rr-security-auditor**
- MR inline POST alone → **rr-ci** after **rr-review** `--ci`

## Constraints

- Dedicated test paths excluded from production findings
- Review maps via `refs/compliance-rubric.md` + `refs/severity-triage.md`
- Fix path is inline in the parent session
- Loaded with `disable-model-invocation: true` / `user-invocable: false` — parent **Read** only

## Notes

Load matrix and Required Knowledge live in [SKILL.md](SKILL.md). **rr-tester** may load this skill so test code matches implementation rules.
