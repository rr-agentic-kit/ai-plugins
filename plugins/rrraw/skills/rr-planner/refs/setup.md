# setup

**Owner:** `--setup` bootstrap/repair of the plans directory. Section names reused by resolve rewrite/sync.

**Load when:** `payload.action` is `setup`; resolve when rewrite or `--sync-agent-config` already runs (same section names). Phrases: [progress.md](progress.md).

`--setup` is primary-only. It never starts discover/compose. First compose remains the safety net if setup was skipped.

## Invoke

```bash
python3 scripts/validate_planning.py --setup --repo-root <PROJECT_ROOT> <plans-dir>
```

Default `plans-dir` = `{PROJECT_ROOT}/docs/plans/`. Create the dir if missing. Do **not** invent cascade docs or empty `future.md`. Do **not** create missing root SoT files.

Script stdout: one machine line per section (`section\tcreated|fixed|ok|failed\tmessage`). Map to [progress.md](progress.md). Fail a section → that section `failed`; later sections still run; overall exit non-zero if any failed.

## Sections

| Section | Created | Fixed | was ok |
|---------|---------|-------|--------|
| `plans directory` | mkdir | — | exists |
| `root SoT load line` | — (never create missing CLAUDE/AGENTS) | append/restore line | already present (or no root SoT files) |
| `agent.plan.md` | write from `refs/agent.plan.md` | overwrite if version lag / body mismatch | matches template |
| `status.yaml` | mint unfrozen `0.1.0?` | fill missing keys only; never bump track | complete + `mint_hash` |
| `cascade format` | — | `--rewrite` list-meta/yaml→md | already canonical **or no docs** |
| `cascade versioning` | insert `track`/`doc_rev`/`pins`/`created` | drop `version`/`traces_from`; align with status | already canonical **or no docs** |

Stub `version: 1` / `traces_from` is discarded, not treated as `doc_rev: 1`. Missing status → mint `track: "0.1"`, `product`/`docs: "0.1.0?"`, all `rev: "?"`. Integer revs only if `status.yaml` already has them. Do not re-freeze.

`status.yaml` / `agent.plan.md` alone do **not** count as in-progress discover — later `--discover` still routes `from-0` until a cascade `{stem}.md` exists ([input-resolution.md](input-resolution.md)).

## Done-when

All six sections reported. No cascade files invented. Existing root SoT files carry the load line. `status.yaml` is complete with `mint_hash`. Project `agent.plan.md` matches the template. Stop. Do not posture. Do not start discover.
