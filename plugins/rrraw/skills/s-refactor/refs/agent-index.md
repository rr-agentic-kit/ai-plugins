# Refactor agent index

**Purpose:** Map `Task` `subagent_type` to agent files. All paths relative to **rrraw** `PLUGIN_ROOT`.

| `subagent_type` | Agent file | `STAGE` | Role |
|-----------------|------------|---------|------|
| `refactor-collector` | `agents/refactor/collector.md` | `assess` | JSON findings only; no source edits |

Fix execution is **inline** — orchestrator **`Read`**s `agents/refactor/fix.md`; **no row** in this table.

Each agent loads only paths from **`leaf-contract.md`** and its own **Load first** section — all under **rrraw** `PLUGIN_ROOT`.
