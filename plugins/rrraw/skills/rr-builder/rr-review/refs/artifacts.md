# Review artifacts

**Purpose:** Sole path + filename + body-template index for **rr-review** runs. Nested skills and severity refs **point here**; do not invent a second path table.

**Disk write contract:** Mint **`runId`** once. Every lane uses the same **`REVIEW_DIR`**. `mkdir -p` via Shell; persist markdown with Write. Paths are at the **repository root** of the project under review.

## Run id

**Format:** `yyyymmdd-NN` — local calendar date + zero-padded daily counter starting at `01`.

**Mint:** List existing `.ai/review/yyyymmdd-*` dirs for today; next = max `NN` + 1 (or `01` if none). No hour/minute.

## Scratch vs terminal

| Layer | Path | Role |
|-------|------|------|
| **Scratch** | `.ai/review/{runId}/` | Brief, assess, challenge, fixing-plan, in-run `report.md` — always |
| **Task terminal** | `docs/rr/tasks/{slice_id}/{NNNN}-{step}.review.md` | Orchestrate review when parent supplies `slice_id` + `{NNNN}` + step cursor — **Write** after endless success (same body skeleton as `report.md`) |
| **Handoff terminal** | `REVIEW_DIR/report.md` | Explicit `--review` **without** task/step cursor — keep scratch report as the announce path |

Optional Steps pointer on `{NNNN}.md`: `→ review: \`{NNNN}-{step}.review.md\``.

## Layout (scratch)

| Rule | Value |
|------|--------|
| Root | `.ai/review/{runId}/` |
| `REVIEW_DIR` | Alias for `.ai/review/{runId}/` |
| Lane dirs | **None** — all files flat under the run dir |
| Filename | Locked type stem only — **do not** embed `runId` or short-branch |
| Multi-chunk | Suffix assess (and its challenge sidecar) with chunk slug (`/` → `--`) |
| Endless | Suffix assess (and challenge) with epoch: `code-assess-e{n}.md` / `code-assess-e{n}-challenge.md` (`n` = 1-based epoch). Multi-chunk + endless: `code-assess-e{n}-<chunk>.md`. Scratch `report.md` overwritten each epoch |

```
.ai/review/{runId}/
  brief.md
  code-assess.md                 # multi-chunk: code-assess-<chunk>.md
  test-assess.md                 # multi-chunk: test-assess-<chunk>.md
  security-audit.md              # multi-chunk: security-audit-<chunk>.md
  code-assess-e1.md              # endless epoch stems (e{n}); non-endless uses unsuffixed
  fixing-plan.md                 # when outcome=fix and scope is large
  report.md                      # scratch merge; overwritten each endless epoch
  scope-preflight.json           # ci only; json exception to *.md
  code-assess-challenge.md       # {assess-stem}-challenge.md
  test-assess-challenge.md
  security-audit-challenge.md
```

## Path + filename matrix

| Artifact | Filename / path | Body template |
|----------|-----------------|---------------|
| Scratch merged report | `REVIEW_DIR/report.md` | Skeleton below |
| Task terminal (orchestrate) | `docs/rr/tasks/{slice_id}/{NNNN}-{step}.review.md` | Same skeleton as `report.md` |
| CI preflight | `scope-preflight.json` | **rr-ci** envelope — point only; schema owned by rr-ci |
| Brief | `brief.md` | [brief-output.md](brief-output.md) |
| Code assess | `code-assess.md` | Skeleton below — CP emit + [`architecture.md`](../../rr-coder/refs/architecture.md) `## Architecture` |
| Test assess | `test-assess.md` | [`rr-tester/refs/report-template.md`](../../rr-tester/refs/report-template.md) |
| Security | `security-audit.md` | [`rr-security-auditor/SKILL.md`](../../rr-security-auditor/SKILL.md) §Output format |
| Fix plan | `fixing-plan.md` | Skeleton in [fix-routing.md](fix-routing.md) |
| Challenge | `{assess-stem}-challenge.md` | Table in [severity-triage.md](severity-triage.md) |

Multi-chunk examples: `code-assess-src--foo.md` + `code-assess-src--foo-challenge.md`.

Endless examples: `code-assess-e2.md` + `code-assess-e2-challenge.md`; multi-chunk: `code-assess-e2-src--foo.md` + `code-assess-e2-src--foo-challenge.md`.

## Body skeletons

### `report.md` / `{NNNN}-{step}.review.md`

```markdown
# Review report

- **Scope:** <paths / MR|PR / branch>
- **Mode:** report | fix | ci | endless-fix
- **Run id:** <yyyymmdd-NN>
- **Epoch:** <n of max_epochs when endless; else omit>
- **Brief path:** REVIEW_DIR/brief.md
- **Goal source:** <brief GOAL or unresolved>
- **Review decision:** <pass | warnings | blocked | fix-applied | ci-handed-off | max-epochs>
- **Scratch:** `.ai/review/<runId>/` (optional pointer)

## Code
<summary or link to code-assess*.md; keep rows only>

## Test
<summary or link to test-assess*.md; keep rows only>

## Security
<summary or link to security-audit*.md; keep rows only>

## Fix plan
<link to fixing-plan.md when written; else omit>
```

### `code-assess.md`

CP finding table first, then mandatory architecture section (full AR rules: [`architecture.md`](../../rr-coder/refs/architecture.md)):

```markdown
# Code assess

| # | Severity | Rule ID | Location | Issue | Evidence |
|---|----------|---------|----------|-------|----------|

## Architecture
Result: PASS | ISSUES | NOT_APPLICABLE
| ID | severity | target | issue | evidence | recommendation |
```

### `fixing-plan.md`

See [fix-routing.md](fix-routing.md) — checkbox states `- [ ]` / `- [executed]` / `- [verified]` only. No `trp-*` stems.

### Challenge sidecar

Locked filename: **`{assess-stem}-challenge.md`** in the same `REVIEW_DIR` (e.g. `code-assess-challenge.md`). Body = Challenge table in [severity-triage.md](severity-triage.md).

## `.gitignore` (consumer repos)

Recommended: ignore `.ai/` (or at least `.ai/review/` and `.ai/ci/`) for local-only AI output. Task terminals under `docs/rr/tasks/` are durable — do **not** gitignore them.

## Related

- Params: [params.md](params.md)
- Endless: [endless.md](endless.md)
- Brief: [brief-output.md](brief-output.md)
- Fix routing: [fix-routing.md](fix-routing.md)
- Challenge: [severity-triage.md](severity-triage.md)
