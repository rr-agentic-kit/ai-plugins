# Pipeline fix (`--fix`)

Remediate a failed CI job: intake → fetch → locate → reproduce → classify → apply → verify. Load [pipeline-fix-rules.md](pipeline-fix-rules.md) before apply.

## 1. intake

**Input:** run/job URL, PR/MR id, or nothing (current branch's open PR/MR).

**Done:** target recorded (URL, id, or branch fallback). **Stop:** none when a run/job URL is given — URL is sufficient.

## 2. fetch

Run the active forge skill **debug-pipeline** task row with the URL or id; request saved logs and artifacts when logs or artifacts will help locate the failure.

**Done:** envelope has `result.status`, `result.error_lines`, `result.failed_job_id`, `result.failed_job_name`, `result.failed_step`, `result.run_url`. **Stop:** `ok: false` or `status` ∈ `no_pipeline` | `no_failed_job` with no alternate target.

## 3. locate

From the envelope: failing job name, step (when present), and filtered `error_lines`. Cross-check saved log/artifact paths under `.ai/ci/` when present.

**Done:** one failing step + primary error signature identified. **Stop:** multiple unrelated failures — pick the first blocking job or AskQuestion.

## 4. reproduce

Run the failing command locally (or the narrowest test/target from the log). If it cannot be reproduced, record why (env drift, runner-only, flaky timing).

**Done:** reproduced locally **or** documented non-repro with evidence. **Stop:** cannot run locally and no log evidence → escalate.

## 5. classify

Required enum + one-line evidence citation:

| Class | When |
|-------|------|
| `product` | Application bug surfaced by CI |
| `test` | Test wrong, flaky, or missing fixture |
| `workflow` | CI YAML/config wiring (`needs`, matrix, paths) |
| `dependency` | Lockfile, image, or package version |
| `runner-infra` | Runner capacity, network, forge outage, transient flake |

**Done:** class + evidence line recorded. **Stop:** class unknown after one retry → AskQuestion.

## 6. apply

Minimal fix for the classified root cause. Evidence-gated weakening/retries: see [pipeline-fix-rules.md](pipeline-fix-rules.md).

**Done:** fix applied in working tree (and workflow file when `workflow`). **Stop:** only path is disable/bypass/retry without evidence → AskQuestion.

## 7. verify

1. Re-run the failing target locally.
2. Push and poll/re-push per the active forge skill **pre-merge** / **wait** task rows (subset re-run or full pipeline as appropriate).

**Done:** local verify pass **and** pipeline subset green (or user accepts documented infra wait). **Stop:** verify fails twice → stop with classification + logs.

## Output

Report: failing step, classification + evidence, fix summary, verification result (`pass` | `fail` | `pending-infra`).

## TodoWrite ids

`root`, `forge`, `load`, `execute`, `intake`, `fetch`, `locate`, `reproduce`, `classify`, `apply`, `verify` (skip ship `title`; skip `forge` when URL supplies owner/repo).
