# endless_test_helpers

Deterministic orchestration helpers for **`s-test-endless`**. Run from **`PLUGIN_ROOT`** (rrraw plugin root).

## Invoke

```bash
python3 scripts/endless_test_helpers/cli.py <subcommand> [options]
```

| Subcommand | Args | Stdout | Exit |
|------------|------|--------|------|
| `packing-probes` | `--plans-dir <dir>` [`--chunk <id>`] | Probe verdict lines + optional `PACKING_RETRY:` hint | 0 pass; 1 probe fail; 2 parallel_collision |
| `dispatch-queue` | `--plans-dir <dir>` [`--max-parallel N`] | JSON `{ "layers": [...] }` | 0 ok; 1 packing_gate (intersecting batch) |
| `aggregate-counts` | `--assess <path>` (repeatable) | Combined `COUNTS:` + markdown defect table | 0 ok; 1 parse error |
| `manifest-table` | `--plans-dir <dir>` `--iteration <n>` | §3b markdown table block | 0 ok |

Stderr: human-readable errors. Orchestrator branches on exit code and stdout only.

**Dependencies:** stdlib only (no pip install).
