---
name: rr-review
description: Multi-lane review hub — parse lanes, mint run id, brief, chunk, assess via nested skills, Challenge, merge report; --fix inline or --ci handoff to rr-ci. Artifacts under .rr-builder/{runId}/.
disable-model-invocation: true
user-invocable: false
---

# rr-review

**Human overview:** [README.md](README.md)

Orchestrate code / test / security review in the **parent session** (v1: no dedicated review agents). Lane rubrics live in **rr-coder**, **rr-tester**, **rr-security-auditor**.

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
| [refs/maintenance-hunk-exclusion.md](refs/maintenance-hunk-exclusion.md) | Challenge sweep |

## Steps (`todo_id`)

### 1. parse

Confirm param block from [refs/params.md](refs/params.md). Default lanes: `[code, test, security]`. **Abort:** `--fix` + `--ci`; unknown flag.

### 2. id

Mint **`runId`**: `MM-DD-HH-mm-ss` local; collision suffix `-2`, `-3`, … **`REVIEW_DIR`** = `.rr-builder/<runId>/`. `mkdir -p` lane subdirs.

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

### 6. assess

For each chunk × lane, **`Read`** nested skill and produce assess artifact under `REVIEW_DIR` (see [refs/artifacts.md](refs/artifacts.md)). Forward **`BRIEF_PATH`**; when `outcome: ci`, use **`READ_REF`** via `git show` for context reads.

### 7. Challenge

Parent session. **`Read`** [refs/severity-triage.md](refs/severity-triage.md) + lane binding refs + [refs/maintenance-hunk-exclusion.md](refs/maintenance-hunk-exclusion.md). Persist **Challenge** appendix per lane. Consumers use **`keep` only**. Unchallenged challengeable rows → **Stopped:** `unchallenged report`.

### 8. branch (outcome)

| `outcome` | Action |
|-----------|--------|
| `report` | → step 9 |
| `fix` | **`Read`** [refs/fix-routing.md](refs/fix-routing.md) — inline fix per plan; reuse **rr-tester** agents for test lane writes when needed |
| `ci` | **`Read`** `skills/rr-ci/SKILL.md` — inline POST, pipeline security reports, review submit → step 9 |

### 9. merge

Write **`REVIEW_DIR/report.md`** — sections per lane; header: Scope, Mode, Run id, Brief path, Goal source, Review decision. Chat: `Report written: .rr-builder/<runId>/report.md`.

## Stop conditions

- Incompatible flags
- `outcome: ci` + no open PR/MR
- Assess failed for lane needed by `--fix` → skip lane fix; note in report
- `--ci` + unchallenged blocker-tier rows → refuse POST

## When not to use

Standalone PR open or pipeline-only debug → **rr-ci** without review.
