# Pipeline fix rules

Success metric: **correct root-cause fix**, not green at any cost.

## Forbidden without user approval

Do not apply unless the user explicitly approves in this session:

- CI weakening: `allow_failure: true`, `when: manual`, commenting out required jobs
- Deleting tests, scanners, or coverage gates to silence failures
- Skip annotations / `@Disabled` to hide failures
- Catch-all handlers or linter-disable without fixing the issue

## Evidence-gated

Timeout increases, retries, `skip`/quarantine, and CI weakening are **never** the default fix. They require:

1. Classification `runner-infra` or documented transient signature in logs
2. Cited evidence (repro showing flakiness, or known upstream/transient error)
3. Bounded scope — e.g. single-test retry with count ≤ 2, not whole-job retry loops

Without evidence → stop and AskQuestion; do not weaken.

## Allowed

Legitimate YAML/image/variable/`needs` fixes; source and test fixes that preserve behavior. Org/runner/secret blockers → stop and escalate with evidence.

## Gate

If the only path is disable/bypass: stop, present tradeoffs, wait for approval. Default = do not proceed.
