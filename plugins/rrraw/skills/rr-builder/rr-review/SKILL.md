---
name: rr-review
description: "Multi-lane review under .ai/review/<runId>/. Via --review (+ nested flags) or orchestrate review (forces --fix --all --endless)."
disable-model-invocation: true
user-invocable: false
---

# rr-review

**Human overview:** [README.md](README.md)

## Purpose

Orchestrate multi-lane code / test / security review in the **parent session**. Scratch (brief/assess/challenge) lives under **`.ai/review/<runId>/`**. **Orchestrate** with task/step cursor: terminal report → `docs/rr/tasks/{slice_id}/{NNNN}-{step}.review.md`. **Handoff `--review`** without cursor: terminal stays `REVIEW_DIR/report.md`. Lane rubrics live in **rr-coder**, **rr-tester**, **rr-security-auditor**. Optional **`--endless`** loops assess→Challenge→fix→re-assess until clear or epoch cap.

## When to use

- Multi-lane review via **rr-builder** `--review` with nested `--code`, `--test`, `--security`, or `--all`
- Optional nested `--fix` (inline apply), `--endless` (fix loop until clear), or `--ci` (handoff to **rr-ci** after Challenge)
- Builder orchestrate **review** stage — parent **forces** `--fix --all --endless` (engineers wanting report-only use explicit `--review` without `--fix`)
- Review intent from **rr-builder** when `payload.lane` is `review`

## When not to use

Standalone PR open or pipeline-only debug → **rr-ci** without review.

## Load

| Ref | When |
|-----|------|
| [refs/params.md](refs/params.md) | Parse flags |
| [refs/artifacts.md](refs/artifacts.md) | Mint run id, paths |
| [refs/brief-sources.md](refs/brief-sources.md) | Brief discovery |
| [refs/brief-output.md](refs/brief-output.md) | Brief schema |
| [refs/chunking.md](refs/chunking.md) | Large scope |
| [refs/severity-triage.md](refs/severity-triage.md) | Challenge step |
| [refs/fix-routing.md](refs/fix-routing.md) | `--fix` |
| [refs/endless.md](refs/endless.md) | When `endless: true` |
| [refs/maintenance-hunk-exclusion.md](refs/maintenance-hunk-exclusion.md) | Challenge sweep |

## Procedure

TodoWrite `merge: false` with ids matching steps below when the run spans 3+ steps. When `endless`, use `merge: true` per epoch after the first; exactly one `in_progress`.

### 1. parse

Confirm param block from [refs/params.md](refs/params.md). Default lanes: `[code, test, security]`. **Abort:** `--fix` + `--ci`; `--endless` + `--ci`; `--endless` without `--fix` (unless forced); unknown flag.

### 2. id

Mint **`runId`**: `yyyymmdd-NN` local (list today's `.ai/review/yyyymmdd-*`; next = max `NN` + 1, or `01`). **`REVIEW_DIR`** = `.ai/review/<runId>/`. `mkdir -p` **`REVIEW_DIR`** (flat — no lane subdirs). Paths: [refs/artifacts.md](refs/artifacts.md).

### 3. scope

| `outcome` | Behavior |
|-----------|----------|
| `ci` | **Read** `skills/rr-ci/SKILL.md` → nested forge skill → run MR/PR preflight; set **`MERGE_BASE`**, **`ALLOWLIST`**, **`READ_REF`**, diff refs; **Write** `REVIEW_DIR/scope-preflight.json` |
| `report` / `fix` | Local branch: merge-base → `HEAD` file list; workspace **Read** on working tree |

Empty allowlist → ask once or stop.

### 3a. resolve-mr

| `outcome` | MR resolution |
|-----------|---------------|
| `ci` | From rr-ci preflight (no second round-trip) |
| `report` / `fix` | Attempt open PR/MR via rr-ci nested refs; absent → branch + local docs only |

### 3b. brief

Build brief per [refs/brief-sources.md](refs/brief-sources.md) and [refs/brief-output.md](refs/brief-output.md). Optional linked Jira/Confluence misses **must not** block when PR/MR or local docs suffice. Retain **`BRIEF_PATH`** for assess passes.

### 4. chunk

Large scope → [refs/chunking.md](refs/chunking.md). Each chunk: **`CHUNK n/m`**, disjoint **`FILES`**.

### 5. select

Per chunk, ordered lane list:

| Files in chunk | Lanes |
|----------------|-------|
| Production | `code`, `security` if ∈ lanes |
| Production + tests | + `test` when test ∈ lanes |
| Test-only | `test` only |

### 6–9. assess → Challenge → branch → merge

When **`endless: false`**: run steps 6–9 once (below).

When **`endless: true`**: for `epoch = 1..max_epochs`:

1. **assess** (step 6) with epoch-stamped stems (`code-assess-e{n}.md` — [refs/artifacts.md](refs/artifacts.md)).
2. **Challenge** (step 7).
3. Evaluate [refs/endless.md](refs/endless.md) exit rules **before** burning a fix epoch when already clear.
4. If not clear and epoch allows: **fix** (step 8) per [refs/fix-routing.md](refs/fix-routing.md), then continue.
5. **merge** (step 9) — overwrite `report.md` each epoch.
6. On clear / warnings-security-only → exit success. On cap without clear → stop per [refs/endless.md](refs/endless.md) (orchestrate leaves `step_review_done` unset).

#### 6. assess

For each chunk × lane, **`Read`** nested skill and produce assess artifact under `REVIEW_DIR` (see [refs/artifacts.md](refs/artifacts.md)). Forward **`BRIEF_PATH`**; when `outcome: ci`, use **`READ_REF`** via `git show` for context reads.

#### 7. Challenge

Parent session. **`Read`** [refs/severity-triage.md](refs/severity-triage.md) + lane binding refs + [refs/maintenance-hunk-exclusion.md](refs/maintenance-hunk-exclusion.md). Persist **`{assess-stem}-challenge.md`** per lane (see [refs/artifacts.md](refs/artifacts.md)). Consumers use **`keep` only**. Unchallenged challengeable rows → **Stopped:** `unchallenged report`.

#### 8. branch (outcome)

| `outcome` | Action |
|-----------|--------|
| `report` | → step 9 |
| `fix` | **`Read`** [refs/fix-routing.md](refs/fix-routing.md) — inline fix per plan; reuse **rr-tester** agents for test lane writes when needed |
| `ci` | **`Read`** `skills/rr-ci/SKILL.md` — inline POST, pipeline security reports, review submit → step 9 |

#### 9. merge

1. Write **`REVIEW_DIR/report.md`** (scratch) per body skeleton in [refs/artifacts.md](refs/artifacts.md) — sections per lane; header: Scope, Mode, Run id, Brief path, Goal source, Review decision. Overwrite each endless epoch.
2. **Terminal path:**
   - Parent supplies `slice_id` + `{NNNN}` + step (orchestrate review) → also **Write** `docs/rr/tasks/{slice_id}/{NNNN}-{step}.review.md` (same skeleton; optional Steps pointer `→ review: \`…\``). Chat: that task path.
   - Else (handoff `--review` without cursor) → chat: `Report written: .ai/review/<runId>/report.md`.

## Stop conditions

- Incompatible flags
- `outcome: ci` + no open PR/MR
- Assess failed for lane needed by `--fix` → skip lane fix; note in report
- `--ci` + unchallenged blocker-tier rows → refuse POST
- Endless epoch cap without clear/warnings-security-only → stop per [refs/endless.md](refs/endless.md)
