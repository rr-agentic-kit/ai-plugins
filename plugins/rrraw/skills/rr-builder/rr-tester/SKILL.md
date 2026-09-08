---
name: rr-tester
description: Flag-driven test excellence — assess, identify gaps, write/fix/migrate tests, triage flaky. Orchestrates phase agents under agents/test/*; loaded by rr-builder or rr-review test lane.
disable-model-invocation: true
user-invocable: false
---

# rr-tester (runtime)

**Human overview:** [README.md](README.md)

## Purpose

Normalize test flags into a canonical payload, delegate to one `agents/test/*` agent or deterministic phase chain, and emit structured output. Skill owns routing, epoch loops, and exhaustiveness gates — agents execute one phase each.

## When to use

- Test assess, gap identification, write/fix/migrate, flaky triage (via **rr-builder** or **rr-review** test lane)
- `--init` stack discovery and `CLAUDE.md` patch

## When not to use

| Need | Use instead |
|------|-------------|
| Production code standards | **rr-coder** |
| OWASP / secrets audit | **rr-security-auditor** |
| MR inline POST | **rr-ci** after **rr-review** `--ci` |

## Procedure

TodoWrite `merge: false` with ids `resolve`, `load`, `route`, `determinism`, `format` when chain length > 1; single-shot N/A for `--assess` / `--init`.

1. **resolve** — Read [refs/input-resolution.md](refs/input-resolution.md); normalize flags and prompt into canonical payload. Done: payload with exactly one primary action (or `--init` exclusivity satisfied).
2. **load** — Read refs from **Shared refs** table below as each phase requires; do not preload all refs. Done: phase-required refs Read.
3. **route** — Map action to agent or chain (see **Action routing**); invoke via `Task` with `PhaseInput` per [refs/contracts.md](refs/contracts.md). Done: Task invoked with PhaseInput per contracts.md.
4. **determinism** — After each agent, apply hooks in [refs/determinism.md](refs/determinism.md); block completion when verify or oracle gates fail.
5. **format** — Adapt output via [refs/output-formats.md](refs/output-formats.md) for `--output` mode. Done: status + findings per contract.

Agents under `agents/test/*` are function-style executors: they receive normalized payload, return typed output, and do not own routing or continuation. Path fallback: [refs/agent-index.md](refs/agent-index.md).

## Exhaustiveness doctrine

Full rules (enumerate all files, maintain→exclude→add ordering, residual gates, epoch budget): [refs/determinism.md](refs/determinism.md) and [refs/shared-heuristics.md](refs/shared-heuristics.md).

## Action routing

Flag→agent mapping and chain expansion: [refs/input-resolution.md](refs/input-resolution.md) §Primary action flags + §chain expansion.

Multi-phase chain exit rules and orchestration gates: [refs/determinism.md](refs/determinism.md).

## Shared refs (load on demand)

| Ref | Owns |
|-----|------|
| [input-resolution.md](refs/input-resolution.md) | Flag parsing, NL intent, conflict matrix, precedence, normalized payload schema |
| [contracts.md](refs/contracts.md) | Phase input/output/error schemas per agent |
| [determinism.md](refs/determinism.md) | Ordering, retries, epoch exit, merge rules, verify gates |
| [output-formats.md](refs/output-formats.md) | md / text / json adapters; status merge |
| [shared-heuristics.md](refs/shared-heuristics.md) | Cross-phase verdict rules (assess, identify-missing, flaky) |
| [init-mode.md](refs/init-mode.md) | `--init` workflow, question/suggestion protocol, completion criteria |
| [claude-md-schema.md](refs/claude-md-schema.md) | `CLAUDE.md` section contract and idempotent patch rules |
| [report-template.md](refs/report-template.md) | Markdown table schemas for `md` output |
| [coverage-exclusions.md](refs/coverage-exclusions.md) | Non-testable taxonomy, stack exclusion patterns, verify rules |
| [agent-index.md](refs/agent-index.md) | Packaged agent path fallback for Task delegation |
| [test-types.md](refs/test-types.md) | Pyramid and test-type evaluation |
| [java-test.md](refs/java-test.md) | Java/JUnit patterns |
| [python-test.md](refs/python-test.md) | pytest patterns |
| [react-test.md](refs/react-test.md) | React Testing Library |
| [vue-test.md](refs/vue-test.md) | Vue Test Utils |
| [playwright.md](refs/playwright.md) | E2E Playwright |
| [severity-triage.md](refs/severity-triage.md) | Review lane Challenge binding |

Phase-specific tactics stay in `agents/test/*` — skill does not duplicate agent execution steps.
