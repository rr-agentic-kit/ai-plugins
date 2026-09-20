# Refactor fix disposition (inline execute)

**Purpose:** Phase-specific fix rules when executing violation lists (manifest or parent prompt). **Audience:** inline fix per `agents/refactor/fix.md`; not the collector.

Honor collector **`disposition`** on every item. Complete one full pass over all listed items of the **current** violation type before moving to the next. If validation or toolchain fails **twice** for the same edit attempt, mark **`no_progress`** and report.

## God methods (`god_method`, Phase 2)

- Target: ≤20–30 lines per method; extract one logical responsibility per new function.
- **Do not** stop after one extraction — continue until the method meets the target.

## God classes / large modules (`god_class`, Phase 3)

- Split by responsibility; use facades and clear module boundaries where the rubric applies.
- **Continue** until structural findings are **resolved**, not partially.

## Cohesion (`mixed_responsibility`, Phase 4)

- Classify per `srp-cohesion.md` (red/green/gray; new vs live).
- **`fix`** — collapse compat forks / one product API; extract only when needed.
- **`clarify`** — minimal why-comment or ownership note only.
- **`escalate_human`** — no structural edit; report tradeoff to parent.

## Visibility (`visibility`, Phase 6, CP031)

- Apply least-necessary visibility per principles § Visibility / encapsulation.
- **`fix`** — single-step visibility downgrade only; re-verify compile/tests; **do not** change signatures, logic, or delete symbols.
- **`clarify`** — optional minimal ownership note if behavior-invariant; else leave for human.
- **`escalate_human`** — published SPI / reflection / framework DI / multi-artifact / uncertain — **no** silent narrow.

## Dead code / stale docs (`dead_code`, `stale_comment`, `stale_doc`, Phase 7)

- Prefer tool-backed unused removals; treat LLM residual the same when clearly private/local.
- **`fix`** — remove unused import/local/clearly-private helper; fix or remove unambiguous stale comment/nearby doc claim (**CP018** / **CP009**); **do not** change runtime behavior to match a wrong doc.
- **`clarify`** — short note only when doc/code conflict is unclear.
- **`escalate_human`** — public/exported/SPI/reflective/config-driven entry or uncertain liveness (**CP010** when speculative) — **no** silent delete.
- **`naming`:** complete listed items; disposition optional.

## Language / framework (`language_ref`, Phase 8)

- Apply Prefer/Avoid and MUST from loaded stack refs (cite **`CPNNN`** or ref **§heading**).
- **`fix`** — behavior-invariant cleanup only (e.g. JSpecify instead of Jakarta-as-nullness; drop duplicate internal null/blank guards when boundary BV already covers).
- **`clarify`** / **`escalate_human`** — introducing `@Valid` / new BV where requests were previously accepted; flipping service `@Validated`; any change that would alter HTTP/status or thrown validation errors — **do not** apply.
- If a listed **`fix`** would still change observable I/O — treat as semantic conflict: **stop** and escalate.

## Observability (`observability`, Phase 8, CP028–CP030)

- Apply Prefer/Avoid from loaded `observability.md`.
- **`fix`** — hygiene on **existing** log statements only (parameterized/structured form; redact secrets/PII when clearly safe; adjust level/context; clearly local hot-path noise).
- **`clarify`** / **`escalate_human`** — missing meters/spans/`@Observed`/new log sites; inventing trace/request-id propagation; rewriting metric label schemas — **do not** apply.
- If a listed **`fix`** would still change product I/O acceptance — treat as semantic conflict: **stop** and escalate.

## Other violations

Fix per phase/order in the manifest (magic numbers, nesting, DRY, naming). Sonar rows on **test-only** paths: skip (Sonar remediation → **rr-ci**).
