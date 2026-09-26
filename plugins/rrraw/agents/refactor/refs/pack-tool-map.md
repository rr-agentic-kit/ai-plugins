# Pack: tool seed (phases 1–3, 5, 7)

**Band:** `tool_seed` · **Phases:** 1, 2, 3, 5, 7 (tool-covered only)

## Load

1. Read `agents/refactor/refs/tools.md` (Checkstyle / Biome / Spotless → phase tables)
2. Run configured tools once per setup (or re-run after structural phases 1–5 before 6–8)
3. Bucket hits by `phase`; emit seed findings — do **not** invent cohesion / visibility / stack rows from tools

## Checklist

- [ ] Project type known (manifest-first) before choosing runner
- [ ] Java → Checkstyle; JS/TS → Biome; format → Spotless when configured
- [ ] Coupling / class-size → phase **3** only (`god_class`)
- [ ] Unused import/variable → phase **7** (`dead_code`); naming/format → **7** polish
- [ ] Empty tool output ≠ skip mandatory LLM packs for phases **4**, **6**, **7** residual, **8**

## Out of band

Phases **4**, **6**, **8**, and phase **7** residual → `pack-cohesion.md`, `pack-visibility.md`, `pack-dead-docs.md`, `pack-stack-obs.md`.
