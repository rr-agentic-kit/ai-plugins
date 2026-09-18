# rr-prepare input resolution

**Audience:** Every `rr-prepare` invoke (step **resolve**).

## Kernel path

| Input | Action |
|-------|--------|
| Explicit `execute-slice.yaml` path | Load that file |
| `--prepare` / NL without path | Next open pin-complete kernel under `docs/rr/{track}/plan/execute-slice.yaml` (current track from `docs/rr/rrr-status.yaml` / plan `status.yaml`) |
| Missing or unfrozen | **Stop** → **rr-planner** (`execute-handoff` / freeze) |

## Load set (after path resolves)

1. Kernel five fields + `slice_id` + pins (`requirement_ids`, `delta_paths`, constitution/architecture revs, AC refs)
2. Each `delta_paths` file (must exist)
3. Constitution INDEX (always-load standing law)
4. Cited tech ADRs only (on-demand from architecture.md / `adrs/`)
5. AC refs named in pins

Do not load full PRD into context unless a pin forces a specific section.

## Posture classify

Apply [sequencing.md](sequencing.md) table. Emit one of: `greenfield` | `brownfield` | `docs_ahead` | `conflict`.

`conflict` → stop or AskQuestion before L1 (adopt code vs adopt docs). Text-mode: same two options; no stall.

## Output payload (session)

```yaml
kernel_path: string
slice_id: string
track: string
posture: greenfield | brownfield | docs_ahead | conflict
pins: object
pending_tech: []   # filled/updated in tech gate
```

## Stop conditions

- No freeze / incomplete pins / missing delta files
- Planning-only request without prepare intent → **rr-planner**
- Implement intent without prepare → **rr-coder** (parent router)
