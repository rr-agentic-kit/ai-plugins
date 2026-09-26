# Refactor Collector: Tool → Phase Mapping

When Checkstyle, Biome, or Spotless are configured, run them and map output to phases. Use for what they report; LLM packs for gaps (see below).

**Orchestrator:** Prefer one tool pass at setup (seed buckets). Re-run on touched files after structural phases **1–5** before **6–8**. Band pack: `pack-tool-map.md`.

## Checkstyle (Java)

| Checkstyle Rule / Category                          | Phase | Notes |
| --------------------------------------------------- | ----- | ----- |
| MagicNumber, AvoidLiteralsInIfCondition             | **1** | Local clarity — magic numbers/strings |
| SimplifyBooleanExpression, SimplifyBooleanReturn    | **1** | Local clarity — early returns, nesting |
| MethodLength (>20)                                  | **2** | God methods |
| ClassDataAbstractionCoupling, ClassFanOutComplexity | **3** | God classes (size/fan-out) — **not** 4 |
| HiddenField, ParameterAssignment                    | **5** | DRY / duplication hints |
| UnusedImports, UnusedLocalVariable (or similar)     | **7** | `dead_code` — unused imports/locals |
| ConstantName, LocalVariableName, MethodName         | **7** | Naming |

**Run**: `mvn checkstyle:check` or `mvn verify -Dcheckstyle` (if plugin configured)  
**Output**: XML; parse `file`/`line`/`source` (rule key) / `message`

## Biome (JS/TS)

| Biome Rule                                | Phase | Notes |
| ----------------------------------------- | ----- | ----- |
| noMagicNumbers                            | **1** | Local clarity — magic numbers |
| useSimplifiedLogicExpression              | **1** | Local clarity — early returns |
| complexity/noExcessiveCognitiveComplexity | **2** | God methods |
| —                                         | **3** | No direct class-size; LLM via `pack-local-struct.md` |
| —                                         | **4** | No tool substitute — `pack-cohesion.md` |
| noDuplicateParameters                     | **5** | DRY |
| —                                         | **6** | No tool substitute — `pack-visibility.md` |
| noUnusedImports, noUnusedVariables        | **7** | `dead_code` — unused imports/locals/params |
| useNamingConvention                       | **7** | Naming |
| —                                         | **8** | No tool substitute — `pack-stack-obs.md` |

**Run**: `npx biome check .` or `npm run lint` (if biome script)  
**Output**: JSON; parse `diagnostics` with file, line, rule_id, message

## Spotless (Format)

| Spotless          | Phase | Notes |
| ----------------- | ----- | ----- |
| Format violations | **7** | Style/naming polish; low priority |

**Run**: `mvn spotless:check` or `./gradlew spotlessCheck`  
**Output**: Format-only; map to phase 7 as polish. Not primary for SRP/DRY.

## Phase 3 vs 4 (tool boundary)

- **3 (red size):** Coupling / fan-out / >300 LOC — tools above + LLM via `pack-local-struct.md`. Emit `god_class` only here.
- **4 (cohesion):** No tool substitute — `pack-cohesion.md`. Do **not** re-emit LOC/fan-out as cohesion.

## LLM packs (not duplicated here)

| Gap | Pack |
|-----|------|
| Phases 1–3, 5 when tools miss | `pack-local-struct.md` |
| Phase 4 cohesion | `pack-cohesion.md` |
| Phase 6 visibility / CP031 | `pack-visibility.md` |
| Phase 7 residual after unused tools | `pack-dead-docs.md` |
| Phase 8 language + observability | `pack-stack-obs.md` |

**Tool emptiness ≠ skip** mandatory packs for 4 / 6 / 7 residual / 8.
