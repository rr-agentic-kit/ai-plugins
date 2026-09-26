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
