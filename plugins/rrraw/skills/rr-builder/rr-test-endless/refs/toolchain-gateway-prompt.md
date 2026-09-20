# Toolchain gateway — `Task` prompt body

**Load path:** `PLUGIN_ROOT/skills/rr-builder/rr-test-endless/refs/toolchain-gateway-prompt.md`

**Use:** **`rr-test-endless`** orchestration **§7 verify** — **`Task`** **`test-endless-toolchain`** with **`build`** + **`test`** only. **`Read`** this file, substitute **`REPO_ROOT`** in the block below, and pass the result as the **`prompt`** argument with **`subagent_type`:** **`test-endless-toolchain`**, **`description`:** **`Toolchain gateway: build + test`**.

**Substitute:** Replace the literal token **`REPO_ROOT`** below with the absolute repository root (open project under review).

```text
Working directory: REPO_ROOT (repository under review — the open project root).

Phases: build, test only (no lint in this gate). Resolve commands per `skills/rr-builder/rr-test-endless/refs/project-detection.md`.

**Coverage reports** (lcov, HTML, JSON summaries, etc.) are **planning and assessment input** — collect and use them when helpful; **do not** require coverage **threshold** passes to run assess, plan, or fix. This gateway does **not** run **`test:coverage`** as a blocking phase.

Run each phase; stop and report phase name + failure output if any phase fails. Do not proceed to downstream steps on failure.
```
