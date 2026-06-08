---
name: rr-test
description: Flag-driven test excellence — assess, identify gaps, write/fix/migrate tests, triage flaky. Orchestrates phase agents under agents/test/*; no command files, no gate mode.
---

# rr-test (runtime)

**Human overview:** [README.md](README.md)

## Activation

1. Read [refs/input-resolution.md](refs/input-resolution.md) — normalize raw flags and prompt into canonical payload **before** any agent call.
2. Load shared refs on demand per phase (see **Shared refs** below).
3. Route to one agent or deterministic phase chain.
4. Adapt structured phase output to `--output` mode via [refs/output-formats.md](refs/output-formats.md).

Agents under `agents/test/*` are function-style executors: they receive normalized payload, return typed output, and do not own routing or continuation.

## Exhaustiveness doctrine

| Rule | Meaning |
|------|---------|
| **Enumerate all** | Every production + test file in normalized scope gets a row in phase output; no sampling, no "top N". |
| **Complete all plan steps** | Write executes every `maintain` then every `add` step in epoch; unexecuted steps → `status: partial`. |
| **Clean before add** | In `complete-missing`, all `maintain`/`trim`/`redundant` work must complete before any `add` step runs. |
| **Residual = exception** | Exit `ok` only when findings are `fixed` or `wontfix`; anything `flagged` blocks success exit. |
| **Budget exhaustion = failure** | `epoch_budget_exhausted` sets `final_status: partial` and lists all residuals. |

## Primary action flags

Exactly one required per invocation (unless `--init` exclusivity rules apply — see [input-resolution](refs/input-resolution.md)):

| Flag | Agent(s) |
|------|----------|
| `--init` | init-discovery |
| `--assess` | assess |
| `--identify-missing` | identify-missing |
| `--identify-redundant-tests` | assess |
| `--write-tests` | write |
| `--complete-missing-tests` | assess → identify-missing → plan → write → verify → assess (epoch loop) |
| `--generate-test-data` | write |
| `--write-parameterized-tests` | write |
| `--plan-test-strategy` | plan |
| `--design-test-architecture` | plan |
| `--define-testing-pyramid` | plan |
| `--audit-test-performance` | perf-audit |
| `--fix-broken-tests` | fix → verify → optional assess |
| `--refactor-tests` | fix |
| `--migrate-tests` | migrate → verify → assess |
| `--reduce-duplication` | fix |
| `--diagnose-flaky` | flaky |
| `--debug-failing` | debug |

Shared selectors: `--scope`, `--target`, `--output`, `--max-epochs` — normalized by [input-resolution](refs/input-resolution.md); defaults in [README](README.md).

## Runtime flow

```
raw input → input-resolution (normalize) → route(action) → invoke agent(s) → apply determinism hooks → format output
```

### Multi-phase chains (skill-owned)

| Action | Chain |
|--------|-------|
| `--complete-missing-tests` | assess → exit? → identify-missing → plan → write → verify → reassess (epoch loop) |
| `--fix-broken-tests` | fix → verify → assess |
| `--migrate-tests` | migrate → verify → assess |

Epoch exit, verify gates, and reassess rules: [refs/determinism.md](refs/determinism.md).

### Orchestration: exhaustiveness

After each phase in `complete-missing` chains, skill applies these checks before continuing:

1. **Enumeration gate:** Parse `enumeration_complete` from assess and identify-missing — if `false`, hard-stop with `exit_reason: enumeration_incomplete`, `final_status: failed`; do not invoke subsequent phases or start next epoch.
2. **Maintain-before-add gate:** Before write, verify all plan `maintain` steps from prior epochs are `solved`, `fixed`, or `wontfix`; block write `add` track otherwise.
3. **Write completeness gate:** After write, if `steps_skipped` contains entries without `wontfix` in plan constraints → treat write as `partial`; do not declare epoch success.
4. **Residual gate:** After reassess, count `flagged` findings — continue epoch only if count > 0 and `epoch < max_epochs`; exit `ok` only when zero `flagged` (or all `wontfix`).

### Determinism hooks (skill layer)

Apply [refs/determinism.md](refs/determinism.md) after each agent invocation. Skill blocks completion when verify or oracle gates fail.

### Output

| Mode | Ref |
|------|-----|
| `md` (default) | [refs/output-formats.md](refs/output-formats.md) — findings tables + status |
| `text` | Concise bullets via [refs/output-formats.md](refs/output-formats.md) |
| `json` | Full payload + `resolution_trace` |
| `report` | Deprecated alias for `md` |

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

Phase-specific tactics stay in `agents/test/*` — skill does not duplicate agent execution steps.

## Agent delegation

Invoke via `Task` with `PhaseInput` per [refs/contracts.md](refs/contracts.md). Parse agent JSON: one retry on failure, then hard-stop ([determinism](refs/determinism.md)).

| Agent | Path | Contract |
|-------|------|----------|
| init-discovery | `agents/test/init-discovery.md` | [contracts § init-discovery](refs/contracts.md) |
| assess | `agents/test/assess.md` | [contracts § assess](refs/contracts.md) |
| identify-missing | `agents/test/identify-missing.md` | [contracts § identify-missing](refs/contracts.md) |
| plan | `agents/test/plan.md` | [contracts § plan](refs/contracts.md) |
| write | `agents/test/write.md` | [contracts § write](refs/contracts.md) |
| fix | `agents/test/fix.md` | [contracts § fix](refs/contracts.md) |
| migrate | `agents/test/migrate.md` | [contracts § migrate](refs/contracts.md) |
| flaky | `agents/test/flaky.md` | [contracts § flaky](refs/contracts.md) |
| debug | `agents/test/debug.md` | [contracts § debug](refs/contracts.md) |
| perf-audit | `agents/test/perf-audit.md` | [contracts § perf-audit](refs/contracts.md) |
