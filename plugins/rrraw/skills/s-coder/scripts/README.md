# s-coder scripts

## `node_types_probe.py`

Deterministic verdict for TypeScript `process` / `Buffer` / Node ambient misses — replaces multi-step invent of package.json / tsconfig / include checks.

```bash
python3 skills/s-coder/scripts/node_types_probe.py --cwd <pkg-root> [--file path/to/file.ts]
```

**Stdout:** JSON envelope (`command`, `ok`, `result`, `error`).

| `result.verdict` | Agent action |
|------------------|--------------|
| `ready` | Do not install `@types/node`; do not rewrite imports for ambient |
| `missing_dep` | Add `@types/node` with the lockfile package manager |
| `missing_types` | Set `"types": ["node"]` in the active tsconfig (Node/backend only) |
| `file_outside_include` | Extend `include`, or use `node:process` / triple-slash |
| `no_package_json` / `no_tsconfig` | Resolve project root / config first |

Exit `0` on completed probe; `2` on usage/path errors.
