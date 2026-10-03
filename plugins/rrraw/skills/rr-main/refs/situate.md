# rr-main situate

**Audience:** `situate` and `suggest` actions. Status-first orientation — **read-only**. Never mutate docs, session-state, or code.

## Glance order

1. `docs/rr/rrr-status.yaml` — track / phase / summary line if present
2. Phase `status.yaml` under `docs/rr/{track}/discovery/` and/or `docs/rr/{track}/plan/` when present
3. Session checkpoint — only via `sh scripts/session_state.sh view --path {output_dir}/session-state.json` when path is known; **never** full-file `Read` of `session-state.json`
4. Optional builder cursor — high-level only from task status / slice cursor cues if present (no deep task-body load)

Run scripts from **this skill’s plugin root** (same package as `SKILL.md` / `scripts/`).

## Missing docs

If `docs/rr/` or status files are absent: say so plainly. Next Up = `rr-discovery --setup` or install pointers from plugin `README.md`. Still **no execute** from situate/suggest — offer handoff only.

## Suggest output

From situate facts + role (if known), list ≤5 Next Up options as peer invokes (flag form). Prefer advance/challenge/setup over skip. Do not incentivize freeze-by-say-so or silent build.

## Anti-patterns

- No writes to `docs/rr/`, no `session_state.sh` mutators, no validate `--setup` from this skill
- No peer Procedure; no loading peer `refs/` to “finish” status
- No full dump of cascade stems — glance + one-line phase meaning only
