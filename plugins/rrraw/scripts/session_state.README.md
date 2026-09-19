# session-state CLI

**Run** — do not load this script source into agent context.

```sh
sh scripts/session_state.sh view --path docs/rr/0.1/plan/session-state.json
sh scripts/session_state.sh get --path … --keys checkpoint,metadata
sh scripts/session_state.sh append-decision --path … --json '…'
```

## Contract

| Command | Purpose |
|---------|---------|
| `view` | Presets: `resume` (default), `status`, `tail` — never includes `item_registry` |
| `get` | Named top-level keys; `item_registry` blocked unless `--allow-registry` |
| `append-decision` / `append-assumption` | Mutate arrays (assumption upserts by `id`) |
| `set-checkpoint` / `set-metadata` / `set-resolution` | Shallow patches |
| `append-level-fact` / `append-completed` | Append helpers |
| `dump --i-know` | Full file — **anti-pattern** for agents |

Stdout: one JSON envelope `{command, ok, result, error}`. Atomic write via temp + rename.

## Agent stop-rule

Never `Read` whole `session-state.json` into context. Prefer `view`/`get`/mutators. See `refs/planning/output-formats.md` Session checkpoint access budget.
