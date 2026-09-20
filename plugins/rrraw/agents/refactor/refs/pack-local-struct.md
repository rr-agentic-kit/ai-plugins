# Pack: local structure LLM (phases 1–3, 5)

**Band:** with `tool_seed` residual · **Phases:** 1, 2, 3, 5 when tools missing or incomplete

## Load (only if not already in session)

- `skills/rr-builder/rr-coder/refs/code.principles.md` (Prefer/Avoid: magic, early returns, functions <20 lines, DRY at 3+)
- For phase **3**: `skills/rr-builder/rr-coder/refs/compliance-rubric.md` when citing size/fan-out CPs

## Phase checklists

### Phase 1 — local clarity

| Focus | Types | Disposition |
|-------|--------|-------------|
| Magic numbers/strings → named constants; early returns; nesting >2 | `magic_number`, early-return / nesting | Usually `fix` (optional) |

- [ ] Unnamed domain literals → constant/enum (**CP003** when citing)
- [ ] Nested if/else >2 → early return / extract
- One collect covers magic + nesting (former separate bands)

### Phase 2 — god methods

| Focus | Types | Disposition |
|-------|--------|-------------|
| Methods >20 lines / mixed abstraction | `god_method` | Usually `fix` (optional) |

- [ ] Single abstraction level; extract long functions

### Phase 3 — red size

| Focus | Types | Disposition |
|-------|--------|-------------|
| >300 LOC, high fan-out / coupling | `god_class` | Usually `fix` (optional) |

- [ ] Emit size/fan-out **only** here — never as Phase 4 cohesion
- [ ] Tools: ClassFanOut / ClassDataAbstractionCoupling → seed; LLM LOC when tools missing

### Phase 5 — DRY

| Focus | Types | Disposition |
|-------|--------|-------------|
| Identical duplication at **3+** uses | DRY / duplication | Usually `fix` (optional) |

- [ ] Do **not** extract at 2 uses; Prefer/Avoid from principles

## Output shape

`{file, line, phase: 1|2|3|5, type, description, disposition?}` — high-priority first.
