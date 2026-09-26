# Pack: language / framework + observability (phase 8)

**Band:** `polish` (with dead-docs) · **Phase:** 8 · **Mandatory LLM** (no tool substitute)

## Load (setup once; pack assumes already in session)

1. Detected language/framework refs from coder SKILL matrix (e.g. `.java` → `java.md` + version; Spring Boot → `java.spring.md` + `orm-principles.md`)
2. `skills/s-coder/refs/observability.md`
3. `skills/s-coder/refs/compliance-rubric.md` when citing **CP013**, **CP019**–**CP021**, **CP028**–**CP030**

## Scan procedure

1. Against loaded Prefer/Avoid + MUST (boundary nullness, stack idioms)
2. Against observability Prefer/Avoid (established logger/redact; actionable vs vanity; level matrix)
3. Cite **`CPNNN`** when in rubric; else language ref **§heading**
4. Types: `language_ref` for stack Prefer/Avoid; `observability` for CP028–CP030 / `observability.md`

## Disposition gate (required on every finding)

| Value | When |
|-------|------|
| `fix` | Behavior-invariant annotation/contract cleanup (e.g. JSpecify vs Jakarta-as-nullness; drop *duplicate* internal guards when boundary BV covers; remove BV from `domain/` when nullness moves to JSpecify) **or** observability hygiene on **existing** log statements only (parameterized/structured; redact secrets/PII when clearly safe; adjust level/context; clearly local hot-path noise) |
| `clarify` / `escalate_human` | Introducing `@Valid` / new BV; flipping `@Validated`; any change that alters HTTP/status or thrown validation; **missing** meters/spans/`@Observed`/new log sites; inventing trace propagation; rewriting metric label schemas / unbounded cardinality; vanity-series removal — never silent `fix` when observable I/O would change or when adding instrumentation |

## Checklist

- [ ] Tool emptiness ≠ skip
- [ ] Empty array valid only after a real Phase 8 pass with no violations
- [ ] Do not invent meters/spans/new log sites as `fix`

## Output shape

`{file, line, phase: 8, type: "language_ref"|"observability", description, disposition}`
