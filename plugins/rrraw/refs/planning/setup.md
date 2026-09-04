# setup

**Owner:** `--setup` bootstrap/repair of the project `docs/` framework (discovery + plan phases). Section names reused by resolve rewrite/sync.

**Load when:** `payload.action` is `setup`; resolve when rewrite or `--sync-agent-config` already runs (same section names). Phrases: [progress.md](progress.md).

`--setup` is primary-only. It never starts discover/compose. First compose remains the safety net if setup was skipped. Both `rr-discovery` and `rr-planner` invoke the **same** framework setup.

## Invoke

```bash
sh scripts/validate_planning.sh --setup --repo-root <PROJECT_ROOT>
# optional: --docs-root <dir>   # default {PROJECT_ROOT}/docs
```

Do **not** pass a plans-dir positional. Create dirs if missing. Do **not** invent cascade docs or empty `future.md`. Do **not** create missing root SoT files.

Legacy `docs/plans/` (or older `docs/planning/`): **read fallback only** — script announces the new defaults; no auto-migrate.

Script stdout: one machine line per section (`section\tcreated|fixed|ok|failed\tmessage`). Map to [progress.md](progress.md). Fail a section → that section `failed`; later sections still run; overall exit non-zero if any failed.

## Sections

| Section | Created | Fixed | was ok |
|---------|---------|-------|--------|
| `docs root` | mkdir `docs/` | — | exists |
| `discovery directory` | mkdir `docs/discovery/` | — | exists |
| `plan directory` | mkdir `docs/plan/` | — | exists |
| `root SoT load line` | — (never create missing CLAUDE/AGENTS) | append/restore line | already present (or no root SoT files) |
| `agent.plan.md` | write from template under `docs/` | overwrite if version lag / body mismatch | matches template |
| `rrr-status.yaml` | mint summary defaults | fill missing keys only | complete |
| `discovery status.yaml` | mint Discover-stem unfrozen shell | fill missing keys; never bump track | complete + `mint_hash` |
| `plan status.yaml` | mint PRD-only unfrozen shell | fill missing keys; never bump track | complete + `mint_hash` |
| `cascade format` | — | `--rewrite` per phase dir that has cascade docs | already canonical **or no docs** |
| `cascade versioning` | insert `track`/`doc_rev`/`pins`/`created` | drop `version`/`traces_from`; align with phase status | already canonical **or no docs** |

Stub `version: 1` / `traces_from` is discarded, not treated as `doc_rev: 1`. Missing phase status → mint `track: "0.1"`, `product`/`docs: "0.1.0?"`, phase stems `rev: "?"`. Integer revs only if that phase `status.yaml` already has them. Do not re-freeze.

`rrr-status.yaml` / phase `status.yaml` / `agent.plan.md` alone do **not** count as in-progress discover — later `--discover` still routes `from-0` until a cascade `{stem}.md` exists ([input-resolution.md](../../skills/rr-discovery/refs/input-resolution.md)).

Default skill `output_dir`: discovery → `docs/discovery/`; planner → `docs/plan/`.

## Done-when

All sections reported. No cascade files invented. Existing root SoT files carry the load line. Summary + both phase statuses are complete. Project `docs/agent.plan.md` matches the template. Stop. Do not posture. Do not start discover or Plan compose.
