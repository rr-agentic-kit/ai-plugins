# setup

**Owner:** `--setup` bootstrap/repair of the project `docs/rr/` framework (versioned discovery + plan phases). Host repos keep **planning artifacts only** — `--setup` does **not** install host CI/Actions. Mechanical `validate_planning` ownership stays with the **plugin** (skill steps invoke `scripts/validate_planning.sh`). Section names reused by resolve rewrite/sync.

**Load when:** `payload.action` is `setup`; resolve when rewrite or `--sync-agent-config` already runs (same section names). Phrases: [progress.md](progress.md).

`--setup` is primary-only. It never starts discover/compose. First compose remains the safety net if setup was skipped. Both `rr-discovery` and `rr-planner` invoke the **same** framework setup.

## Invoke

```bash
sh scripts/validate_planning.sh --setup --repo-root <PROJECT_ROOT>
# optional: --docs-root <dir>   # default {PROJECT_ROOT}/docs
```

**Plugin root:** Run that script from the **same package root as the loaded skill** (`SKILL.md` → plugin root → `scripts/`). Do not Glob an older `~/.claude/plugins/cache/**/0.0.4-rc-N` sibling. Format disputes: Read `refs/planning/doc-standards/item-schema.md` §Canonical item surface from that same root (batch with the script invoke) — never invent format law from memory or an older cache.

Do **not** pass a plans-dir positional. Create dirs if missing. Do **not** invent cascade docs or empty `future.md`. Do **not** create missing root SoT files.

Legacy layouts (`docs/discovery/`, `docs/plan/`, `docs/plans/`, `docs/planning/`): **auto-migrated** by the `layout migrate` section into `docs/rr/{track}/{phase}/`. Skills may still read legacy paths until migrate runs.

Script stdout: one machine line per section (`section\tcreated|fixed|ok|failed\tmessage`). Map to [progress.md](progress.md). Fail a section → that section `failed`; later sections still run; overall exit non-zero if any failed.

## Sections

| Section | Created | Fixed | was ok |
|---------|---------|-------|--------|
| `docs root` | mkdir `docs/` | — | exists |
| `rr directory` | mkdir `docs/rr/` | — | exists |
| `layout migrate` | — | move legacy phase-first / flat trees into `docs/rr/{track}/{phase}/`; relocate parking | already migrated / nothing to migrate |
| `tasks directory` | mkdir `docs/rr/tasks/` (empty; `registry.yaml` minted on first prepare) | — | exists |
| `discovery directory` | mkdir `docs/rr/{track}/discovery/` | — | exists |
| `plan directory` | mkdir `docs/rr/{track}/plan/` | — | exists |
| `root SoT load line` | — (never create missing CLAUDE/AGENTS) | append/restore line | already present (or no root SoT files) |
| `agent.plan.md` | write from template under `docs/rr/` | overwrite if version lag / body mismatch | matches template |
| `rrr-status.yaml` | mint summary defaults under `docs/rr/` | fill missing keys only | complete |
| `discovery status.yaml` | mint Discover-stem unfrozen shell | fill missing keys; never bump track | complete + `mint_hash` |
| `plan status.yaml` | mint PRD-only unfrozen shell | fill missing keys; never bump track | complete + `mint_hash` |
| `cascade format` | — | `--rewrite` per phase dir (list-meta, `{stem}.yaml`, **`>` → plain leaf body**); **fail** if `STALE_FORMAT` blockquote remains | already canonical **or no docs** |
| `cascade versioning` | insert `track`/`doc_rev`/`pins`/`created` | drop `version`/`traces_from`; align with phase status | already canonical **or no docs** |

Stub `version: 1` / `traces_from` is discarded, not treated as `doc_rev: 1`. Missing phase status → mint `track: "0.1"`, `product`/`docs: "0.1.0?"`, phase stems `rev: "?"`. Integer revs only if that phase `status.yaml` already has them. Do not re-freeze.

`rrr-status.yaml` / phase `status.yaml` / `agent.plan.md` alone do **not** count as in-progress discover — later `--discover` still routes `from-0` until a cascade `{stem}.md` exists ([input-resolution.md](../../skills/rr-discovery/refs/input-resolution.md)).

Default skill `output_dir`: discovery → `docs/rr/{track}/discovery/`; planner → `docs/rr/{track}/plan/`. Next track → `docs/rr/{next}/{phase}/`.

## Plugin-runtime validate (required)

Hand-edits of `track` / frozen `rev` / pins / `mint_hash` must **FAIL when the plugin validates** (`HAND_BUMP`, `STALE_PIN`, `PARENT_UNFROZEN`, `REV_WHILE_OPEN`, maturity codes) — during skill steps that run `validate_planning.sh` (rewrite, compose gates, explicit validate). See [baselines.md](baselines.md) validator matrix.

**Anti-trigger (hosts):** Do **not** install `.github/workflows/rrr-validate-planning.yml` (or equivalents) into consumer/host repos. Do **not** set host `RRR_PLUGIN_ROOT` / `RRR_VALIDATE_SH` for product CI. Do **not** vendor `plugins/rrraw` into the host so Actions can find the script. Validation is a **plugin exclusive** responsibility; the host stores planning results only. Format mistakes are the plugin’s problem to catch when it runs — not the host’s CI.

Optional agent/local preflight from the **plugin package** (same codes):

```bash
sh scripts/validate_planning.sh docs/rr/0.1/discovery
sh scripts/validate_planning.sh docs/rr/0.1/plan
```

## Done-when

All sections reported. No cascade files invented. Existing root SoT files carry the load line. Summary + both phase statuses are complete. Project `docs/rr/agent.plan.md` matches the template. **No** host PR/Actions validate workflow required or installed. Stop. Do not posture. Do not start discover or Plan compose.
