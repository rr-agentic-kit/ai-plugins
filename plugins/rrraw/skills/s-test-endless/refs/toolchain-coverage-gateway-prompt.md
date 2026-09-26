# Toolchain gateway — coverage-first `Task` prompt body

**Load path:** `PLUGIN_ROOT/skills/s-test-endless/refs/toolchain-coverage-gateway-prompt.md`

**Use:** **`rr-builder --add-endless-test`** — the **orchestrator** **`Read`**s this file, substitutes **`REPO_ROOT`** in the block below, and passes the result as the **`prompt`** argument with **`subagent_type`:** **`test-endless-toolchain`**, **`description`:** **`Toolchain gateway: build + test:coverage`** (or equivalent).

**Also used inside** **`orchestration.md`** **§0** when **`n > 1`** (repeat coverage before the next assess cycle).

**Substitute:** Replace the literal token **`REPO_ROOT`** below with the absolute repository root (open project under review).

```text
Working directory: REPO_ROOT (repository under review — the open project root).

Phases: build, test:coverage only (no lint in this gate). Resolve commands per `skills/s-test-endless/refs/project-detection.md`. Caller label test:coverage maps to the stack's coverage script when present.

**Coverage thresholds:** Global threshold failures are **planning input**, not a hard gate for the endless-add-test orchestrator — run phases, capture logs and any emitted coverage artifacts (lcov, HTML, JSON summaries). If **build** fails or **tests do not execute**, that is a **hard** failure: stop and report phase name + output.

Run each phase in order. Do not skip **build** when the stack requires it for coverage.
```
