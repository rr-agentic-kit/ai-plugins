# Pack: dead code + stale docs residual (phase 7)

**Band:** `polish` (with stack-obs) · **Phase:** 7 residual · **Mandatory LLM after tools**

## Load (only if not already in session)

- `skills/rr-builder/rr-coder/refs/compliance-rubric.md` when citing **CP009** / **CP018** / **CP010**
- Tool seeds for unused/naming already from `pack-tool-map.md` / `tools.md`

## Procedure

1. Start from tool `dead_code` / `naming` seeds (do not re-run full tool suite unless orchestrator asks)
2. LLM residual: unused private helpers/locals/params tools missed
3. Stale/redundant/what-comments → `stale_comment` (**CP018** / **CP009**)
4. Nearby README/module docs that clearly contradict scoped code → `stale_doc` (docs scope = **nearby** only)
5. Naming/format polish → `naming`

## Disposition

| Types | Required? | Values |
|-------|-----------|--------|
| `dead_code`, `stale_doc` | **Required** | `fix` — unused import/local / clearly private helper / unambiguous stale doc (update or remove claim; do **not** change product behavior to match wrong doc). `clarify` — doc/code conflict unclear. `escalate_human` — public/exported/SPI/reflection/config-driven or uncertain live |
| `naming`, `stale_comment` | Optional | — |

## Checklist

- [ ] Tool emptiness ≠ skip residual
- [ ] Empty array valid only after a real LLM residual pass
- [ ] Never silent-delete uncertain public surface

## Output shape

`{file, line, phase: 7, type, description, disposition?}`
