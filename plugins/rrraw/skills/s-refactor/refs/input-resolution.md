# s-refactor input resolution

**Audience:** Parent **rr-builder** when `lane: refactor`. Normalize flags into `payload.refactor`.

## Flags (from parent `--refactor`)

Grammar and validation: **`refs/params.md`** (canonical scope rules — do not duplicate MR recipe here).

| Flag | Field | Default |
|------|-------|---------|
| `--scope MR\|PR\|all\|full` | `scope` | `MR` |
| `--epoch-cap N` | `epoch_cap` | **5** |
| `--sonar-seed PATH` | `sonar_seed` | `null` (set by **s-ci** `--fix --sonar`, not by rr-builder) |
| repo-relative paths | `paths` | `[]` (after scope resolution) |

## Parent payload mapping

| Parent field | Param block field |
|--------------|-------------------|
| `payload.refactor.scope` | `scope` |
| `payload.refactor.paths` | `paths` |
| `payload.refactor.epoch_cap` | `epoch_cap` |
| `payload.refactor.sonar_seed` | `sonar_seed` |

Scope resolution (MR merge-base recipe, production-source filter, positional narrowers, empty-diff clarify): **`refs/params.md`** § Scope.

## Orchestrate refactor stage (parent-built payload)

When builder runs **refactor** stage (not handoff), parent pre-resolves scope:

1. MR file list (s-review recipe — see **`refs/params.md`**).
2. Intersect with files touched during current step **build** + **review** (`git diff` since pre-build snapshot or merge-base + step path hints from `{NNNN}-{step}.plan.md`).
3. Empty intersection → parent **skips** refactor with note; sets `step_refactor_done: true` without loading this skill.
4. Non-empty → pass as `payload.refactor.paths` + `scope: MR`.

## Validation

| Condition | Result |
|-----------|--------|
| Invalid `--epoch-cap` | **Stopped:** `invalid --epoch-cap` |
| Invalid `--sonar-seed` | **Stopped:** `invalid --sonar-seed` |
| Unknown flag | **Stopped:** one-line error |
| Conflicting scope selectors | **Stopped:** `conflicting scope selectors` |
| Non-existent path | **Stopped:** one-line error |
| `--refactor` + another lane flag | Parent stops: `one lane flag only` |

## Output block

```yaml
refactor:
  scope: MR | all
  paths: []
  epoch_cap: 5
  sonar_seed: null
```

Parent sets `payload.lane: refactor` and ignores `drive` / `scope` orchestrate axes.
