# Pipeline fix rules

Success metric: **correct root-cause fix**, not green at any cost.

## Forbidden without user approval

Do not apply unless the user explicitly approves in this session:

- CI weakening: `allow_failure: true`, `when: manual`, commenting out required jobs
- Deleting tests, scanners, or coverage gates to silence failures
- Skip annotations / `@Disabled` to hide failures
- Catch-all handlers or linter-disable without fixing the issue

## Allowed

Legitimate YAML/image/variable/`needs` fixes; source and test fixes that preserve behavior. Org/runner/secret blockers → stop and escalate with evidence.

## Gate

If the only path is disable/bypass: stop, present tradeoffs, wait for approval. Default = do not proceed.

## Classify before unblocking (PR CI)

After reading the **failing job log**, compare **live PR state** on the same tip (`gh pr view` labels/checks; `gh pr checks` may list multiple runs with the **same check name**).

| Class | Signals | Fix path |
|-------|---------|----------|
| **Code / test** | Failure references repo paths, tests, lint, types | Edit branch; narrow local verify; one push |
| **Workflow / config** | YAML, triggers, `needs`, env, duplicate job names across workflows | Edit `.github/workflows` (or equivalent); no empty-commit workaround as the only change |
| **Stale event** | Log says a gate failed (e.g. missing label) but live PR already satisfies it; or one workflow run **pass** and another **fail** for the same check name on one SHA | Root cause is workflow design or label timing — fix workflows or apply labels before first push; **do not** treat `gh run rerun` or an empty `synchronize` commit as the root-cause fix |

**Stop-rule:** `gh run rerun` and empty commits only **replay or refresh** the triggering `pull_request` event payload. They do not repair a broken workflow split. If classification is **stale event** or **workflow / config**, stop symptom pushes and implement the workflow fix (or report the architecture issue) unless the user explicitly asked for a one-off unblock only.
