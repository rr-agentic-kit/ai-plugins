# Test-endless agent index

**Purpose:** Map `Task` `subagent_type` to agent files. All paths relative to **rrraw** `PLUGIN_ROOT`.

| `subagent_type` | Agent file | `STAGE` | Role |
|-----------------|------------|---------|------|
| `test-endless-toolchain` | `agents/test-endless/toolchain.md` | `toolchain` | `build` + `test:coverage` (gateway) or `build` + `test` (verify) |
| `test-endless-assess` | `agents/test-endless/assess.md` | `assess` | Write `tra-*.md`, `COUNTS:` |
| `test-endless-plan` | `agents/test-endless/plan.md` | `plan` | Write `trp-*.md` work-packs |
| `test-endless-fix` | `agents/test-endless/fix.md` | `fix` | Execute one pack; JSON `{success}` |

Each agent loads only paths from **`leaf-contract.md`** and its own **Load first** section — all under **rrraw** `PLUGIN_ROOT`.
