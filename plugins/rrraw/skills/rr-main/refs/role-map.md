# rr-main role map

**Audience:** `orient` / `explain` when filtering “most useful” invokes. Not every flag — curated cheat sheets. Pointers only; peer README owns Procedure.

## Roles

| Role | Who | Default lens |
|------|-----|--------------|
| `founder-pm` | Founder / PM | Prove bet → Plan slice |
| `engineer` | Implementer | Build slice / feature / lane |
| `operator` | Ship / forge / local git | CI, PR/MR, deploy, local git |

When orient has no role and a short filter helps, AskQuestion once: Founder-PM | Engineer | Operator | Skip filter.

## Founder-PM

| Invoke | When |
|--------|------|
| `rr-discovery --setup` | Bootstrap / repair `docs/` framework |
| `rr-discovery --discover` | New or continue Discover through BRD |
| `rr-discovery --challenge` | Pre-mortem / red-team on Discover stems |
| `rr-planner --prd` | Compose PRD+ after frozen business-case |
| `rr-planner --intake` | Absorb idea / coverage into Plan docs+select |
| `rr-planner --freeze-slice` | Mint buildable `execute-slice.yaml` |
| `rr-planner --challenge` | Challenge Plan targets |

Peer indexes: `skills/rr-discovery/README.md`, `skills/rr-planner/README.md`.

## Engineer

| Invoke | When |
|--------|------|
| `rr-builder` (defaults) | Advance frozen slice (`auto` × `step`) |
| `rr-builder --feature` | Planned post-pipeline mint → task-validate |
| `rr-builder --adhoc` | Urgent / unplanned wrap (same gates) |
| `rr-builder --intake` | Docs→task pipeline walk (peer planner for Plan stages) |
| `rr-builder --coder` / `--tester` / `--review` / `--refactor` | Single-lane when scoped |

Peer index: `skills/rr-builder/README.md`. Nested lanes are path-loaded by builder; prefer builder flags over raw `@s-*` unless the user already knows the lane.

## Operator

| Invoke | When |
|--------|------|
| `s-ci` | PR/MR ship, pipeline debug, Sonar fix, Dependabot pull |
| `s-git` | Local git only (rebase, worktree, squash, conflicts) |
| `s-gh` / `s-glab` | Forge-specific when already on that host |
| `s-deploy` / `s-publish` | Deploy or publish as listed in manifests |

Peer indexes: `skills/s-ci/README.md`, `skills/s-git/README.md`, and nested forge/publish/deploy READMEs under `skills/`.

## Anti-patterns

- Do not paste peer Procedure into the cheat sheet
- Do not list skills absent from `plugin.json` `skills[]`
- Do not imply Operator owns Discover/Plan freeze
