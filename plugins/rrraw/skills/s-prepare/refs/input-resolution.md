# s-prepare input resolution

**Audience:** Every `s-prepare` invoke (step **resolve**).

## Kernel path

| Input | Action |
|-------|--------|
| Explicit `execute-slice.yaml` path | Load that file |
| `--prepare` / NL without path | Prefer asking parent for an explicit path. If still omitted: read current track from `docs/rr/rrr-status.yaml` / plan `status.yaml` → open that track’s `docs/rr/{track}/plan/execute-slice.yaml` only if pin-complete → else **Stop** → **rr-planner**. Emit one `kernel_path` (or empty→stop). **Do not** glob-dump plan trees into context for the LLM to filter. |
| Missing or unfrozen | **Stop** → **rr-planner** (`execute-handoff` / freeze) |

## Load set (after path resolves)

1. Kernel five fields + `slice_id` + pins (`requirement_ids`, `delta_paths`, constitution/architecture revs, AC refs)
2. Each `delta_paths` file (must exist)
3. Constitution INDEX (always-load standing law)
4. Cited tech ADRs only (on-demand from architecture.md / `adrs/`)
5. AC refs named in pins

Do not load full PRD into context unless a pin forces a specific section.

## Posture classify

Apply [sequencing.md](sequencing.md) posture table (tokens `greenfield` \| `brownfield` \| `docs_ahead` \| `conflict`, including **conflict** stop/AskQuestion). Emit exactly one of those four tokens.

## Output payload (session)

```yaml
kernel_path: string
slice_id: string
track: string
posture: greenfield | brownfield | docs_ahead | conflict
pins: object
pending_tech: []   # filled in tech gate; [] or list of {topic, blocked_task_ids, status}
```

## Stop conditions

- No freeze / incomplete pins / missing delta files
- Planning-only request without prepare intent → **rr-planner**
- Implement intent without prepare → **s-coder** (parent router)
