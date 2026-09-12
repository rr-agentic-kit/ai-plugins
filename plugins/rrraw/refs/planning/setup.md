# setup

**Owner:** `--setup` bootstrap/repair of the project `docs/rr/` framework (versioned discovery + plan phases) **and** host-repo **PR-scoped** `validate_planning` wire. Section names reused by resolve rewrite/sync.

**Load when:** `payload.action` is `setup`; resolve when rewrite or `--sync-agent-config` already runs (same section names). Phrases: [progress.md](progress.md).

`--setup` is primary-only. It never starts discover/compose. First compose remains the safety net if setup was skipped. Both `rr-discovery` and `rr-planner` invoke the **same** framework setup.

## Invoke

```bash
sh scripts/validate_planning.sh --setup --repo-root <PROJECT_ROOT>
# optional: --docs-root <dir>   # default {PROJECT_ROOT}/docs
```

Do **not** pass a plans-dir positional. Create dirs if missing. Do **not** invent cascade docs or empty `future.md`. Do **not** create missing root SoT files.

Legacy layouts (`docs/discovery/`, `docs/plan/`, `docs/plans/`, `docs/planning/`): **auto-migrated** by the `layout migrate` section into `docs/rr/{track}/{phase}/`. Skills may still read legacy paths until migrate runs.

Script stdout: one machine line per section (`section\tcreated|fixed|ok|failed\tmessage`). Map to [progress.md](progress.md). Fail a section → that section `failed`; later sections still run; overall exit non-zero if any failed.

## Sections

| Section | Created | Fixed | was ok |
|---------|---------|-------|--------|
| `docs root` | mkdir `docs/` | — | exists |
| `rr directory` | mkdir `docs/rr/` | — | exists |
| `layout migrate` | — | move legacy phase-first / flat trees into `docs/rr/{track}/{phase}/`; relocate parking | already migrated / nothing to migrate |
| `tasks directory` | mkdir `docs/rr/tasks/` (empty; reserved) | — | exists |
| `discovery directory` | mkdir `docs/rr/{track}/discovery/` | — | exists |
| `plan directory` | mkdir `docs/rr/{track}/plan/` | — | exists |
| `root SoT load line` | — (never create missing CLAUDE/AGENTS) | append/restore line | already present (or no root SoT files) |
| `agent.plan.md` | write from template under `docs/rr/` | overwrite if version lag / body mismatch | matches template |
| `rrr-status.yaml` | mint summary defaults under `docs/rr/` | fill missing keys only | complete |
| `discovery status.yaml` | mint Discover-stem unfrozen shell | fill missing keys; never bump track | complete + `mint_hash` |
| `plan status.yaml` | mint PRD-only unfrozen shell | fill missing keys; never bump track | complete + `mint_hash` |
| `cascade format` | — | `--rewrite` per phase dir that has cascade docs | already canonical **or no docs** |
| `cascade versioning` | insert `track`/`doc_rev`/`pins`/`created` | drop `version`/`traces_from`; align with phase status | already canonical **or no docs** |
| `pr validate workflow` | write `.github/workflows/rrr-validate-planning.yml` | overwrite if template drift | matches template |

Stub `version: 1` / `traces_from` is discarded, not treated as `doc_rev: 1`. Missing phase status → mint `track: "0.1"`, `product`/`docs: "0.1.0?"`, phase stems `rev: "?"`. Integer revs only if that phase `status.yaml` already has them. Do not re-freeze.

`rrr-status.yaml` / phase `status.yaml` / `agent.plan.md` alone do **not** count as in-progress discover — later `--discover` still routes `from-0` until a cascade `{stem}.md` exists ([input-resolution.md](../../skills/rr-discovery/refs/input-resolution.md)).

Default skill `output_dir`: discovery → `docs/rr/{track}/discovery/`; planner → `docs/rr/{track}/plan/`. Next track → `docs/rr/{next}/{phase}/`.

## PR-scoped validate (required)

Hand-edits of `track` / frozen `rev` / pins / `mint_hash` must **FAIL the PR merge** (`HAND_BUMP`, `STALE_PIN`, `PARENT_UNFROZEN`, `REV_WHILE_OPEN`, maturity codes). Ambient local-only validation is **insufficient** — see [baselines.md](baselines.md) CI matrix.

`--setup` installs `.github/workflows/rrr-validate-planning.yml` from [ci/validate-planning.github.yml](ci/validate-planning.github.yml):

- Triggers on PRs touching `docs/rr/**`
- Discovers track dirs under `docs/rr/` matching `TRACK_DIR_RE`; runs `validate_planning.sh` on each track’s `discovery/` and/or `plan/` phase dirs
- Does **not** mint or classify track major/minor

Script resolution (workflow env, first hit wins):

1. `RRR_VALIDATE_SH` — absolute path to `validate_planning.sh`
2. `RRR_PLUGIN_ROOT/scripts/validate_planning.sh` when `RRR_PLUGIN_ROOT` is set (repo var / secret)
3. `plugins/rrraw/scripts/validate_planning.sh` (monorepo checkout)
4. Else job fails with a clear “set RRR_PLUGIN_ROOT or RRR_VALIDATE_SH” message

Optional local preflight (same codes, not a substitute for PR CI):

```bash
sh scripts/validate_planning.sh docs/rr/0.1/discovery
sh scripts/validate_planning.sh docs/rr/0.1/plan
```

Hosts without GitHub Actions still must wire an equivalent PR/MR check that runs the same script and fails closed on those codes.

## Done-when

All sections reported. No cascade files invented. Existing root SoT files carry the load line. Summary + both phase statuses are complete. Project `docs/rr/agent.plan.md` matches the template. PR validate workflow is present (or host uses a documented equivalent). Stop. Do not posture. Do not start discover or Plan compose.
