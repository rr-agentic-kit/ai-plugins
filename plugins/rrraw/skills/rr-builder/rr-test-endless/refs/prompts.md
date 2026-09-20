# Test-review prompts (polyglot)

**Purpose:** **`Task`** prompt bodies (including **CHUNK_SCOPE** block). **Callback contracts (canonical):** **`orchestration-core.md`** § Callback contracts — do not duplicate shapes here.

Load when the **test-review fix-flow command** (or VCA parent) dispatches **`Task`** to **`test-endless-assess`**, **`test-endless-plan`**, or **`test-endless-fix`** with the leaf contract per **`leaf-contract.md`**.

The **fix-flow command runner** appends a **CHUNK_SCOPE** block to **Assess**, **Re-assess**, and **Plan** prompts (after the body instructions, before the model answers):

```text
CHUNK_SCOPE:
  chunk_id: "<stable id from refs/chunking.md>"
  path_prefixes:
    - "<repo-relative prefix 1>"
    - "<repo-relative prefix 2>"
```

Executors receive **`plan_path`**, **`branch_name`**, **`REPO_ROOT`**, **`PLUGIN_ROOT`**, **`REVIEW_ID`**, **`REVIEW_DIR`**, and **`<base>`** (integration branch — **never** `master`/`main`) — see **`skills/rr-builder/rr-test-endless/refs/artifacts.md`** and **`orchestration-core.md`** Pre-flight §1.

**Execute batching:** One plan file = one work-pack = one worker **`Task`**. The **planner** packs per **`skills/rr-builder/rr-test-endless/refs/work-pack-sizing.md`**; the runner dispatches from YAML with **`--max-parallel`** cap.

**Read order:** Each leaf agent loads its own refs per **`agents/review/review-*-agent.md`**. The command runner supplies paths, **`REVIEW_ID`**, **`REVIEW_DIR`**, and scope.

---

## Verification vs coverage data

- **Toolchain gateway and §7 verify** (orchestrator **`test-endless-toolchain`**) are **`build`** + **`test`** only. **Default test-review fix** pre-read / §7: **`toolchain-gateway-prompt.md`** and **`skills/rr-builder/rr-test-endless/refs/orchestration.md`** §7. **`rr-builder --add-endless-test`** iteration-1 **coverage** gateway (and **`orchestration.md`** §0 when **`n > 1`**): **`toolchain-coverage-gateway-prompt.md`** — do not substitute the wrong file when copying prompts.
- **Coverage outputs** (reports, summaries, uncovered ranges, file-level stats) are **first-class input** to **assess**, **plan**, and **prioritize steps** — use them whenever artifacts exist, **whether or not** line/branch/global **thresholds** are met. **Threshold red is not a reason to skip planning**; sub-threshold gaps are often **more** important to surface in plans.
- If a **coverage collection** command (e.g. **`test:coverage`**) is run for data and exits **non-zero** only because of **threshold enforcement**, the test-review session **still** **Read**s and uses generated outputs for assessment/planning — that failure **must not** be treated as blocking the lane **after** the **`build`**+**`test`** gateway has passed. Prefer ecosystem modes that **emit reports without failing** on thresholds when **`project-detection.md`** / stack refs allow.

---

## Naming preset (test-review worker)

| Field | Value |
|--------|--------|
| `<base>` | **Integration branch** (merge target): **local** branch name from pre-flight **`git branch --show-current`** per **`skills/rr-builder/rr-test-endless/refs/orchestration.md`** / **`orchestration.md`** Pre-flight §1 — **never** `master` or `main` (ASCII case-insensitive). Worker **refuses** trunk; orchestrator **hard-stops** if still on trunk. |
| `<branch_name>` | YAML frontmatter **`branch:`** on the plan file. **One** git branch + worktree per worker **`Task`**. See **`skills/rr-builder/rr-test-endless/refs/orchestration.md`** §4. |
| `<worktree_path>` | `../{project-name}-{branch_name}` (sibling to repo, **not** inside it) |
| `<phase>` | `test-review` |

`{project-name}` = `basename REPO_ROOT`. The worker creates **one** worktree per **`Task`**, executes all **`## Steps`** in list order, then rebases + ff-merges **`branch_name`** into **`<base>`** (integration branch only).

---

## Assess (orchestrator)

**Subagent:** **`test-endless-assess`** — **`STAGE=assess`**, **`EVAL=test`** (singleton for endless add-test — see **`leaf-contract.md`**).

**Command runner supplies:** **`REVIEW_ID`**, **`REVIEW_DIR`**, **`REPO_ROOT`**, **`PLUGIN_ROOT`**, **`Scope:`** / narrative, **CHUNK_SCOPE**, **`FILES`** derived from chunk scope.

**Prompt body (minimal — agent loads refs via `LOAD` / eval profile):**

```text
STAGE=assess
EVAL=test
REVIEW_ID=<reviewId>
REVIEW_DIR=.ai/review/<reviewId>
BRIEF_PATH=<path from brief stage, or omit when none>
FILES: (from CHUNK_SCOPE path_prefixes — or list explicitly)

Orchestrator-mode assess for test-review fix flow.

CHUNK_SCOPE: (command appends block below)

Evaluate production under CHUNK_SCOPE path_prefixes only (live-assess). Exhaustive per assess-output.md and test-heuristics.md — 100% of in-scope methods and branches; ADEQUATE count only on COUNTS line.

Write assessment under REVIEW_DIR/test/assess/tra-<short-branch>-<REVIEW_ID>[-<chunk>].md (mkdir -p via Shell; Write body per assess-output.md). Final chat line(s) only per orchestration-core.md Callback contracts (Assessor) — one Report written: per artifact when parent bundled multiple EVALs.

PLUGIN_ROOT=<absolute>
REPO_ROOT=<absolute>
```

**Callback:** **`orchestration-core.md`** § Callback contracts (Assessor). Parent may bundle lanes; expect one **`Report written:`** line per assess artifact.

---

## Re-assess (orchestrator)

Same **`test-endless-assess`** contract as **Assess**, with prior iteration’s assessment file path (or copy under **`REVIEW_DIR/test/state/`**) when the command runner kept it. Forward the same **`BRIEF_PATH`** as the initial assess. Prompt must request **`RE-ASSESS DIFF`** section per **assess-output.md** when applicable.

---

## Plan

**Subagent:** **`test-endless-plan`** — **`STAGE=plan`** (no **`EVAL`**).

**Command runner supplies:** **full assessment path list** (every chunk × every lane from assess **`Report written:`** lines), **`REVIEW_ID`**, **`REVIEW_DIR`**, **`REPO_ROOT`**, **`PLUGIN_ROOT`**, optional **CHUNK_SCOPE** blocks for disambiguation.

**Prompt body** (for **`rr-builder --add-endless-test`** orchestrator):

```text
STAGE=plan
REVIEW_ID=<reviewId>
REVIEW_DIR=.ai/review/<reviewId>

ASSESSMENT_PATHS:
<one path per line — all assess artifacts this round>

Plan remediation from kept findings only. Assessment-bound planning per agents/test-endless/plan.md and work-pack-sizing.md.

Produce one or more markdown plans under REVIEW_DIR/plans/ (mkdir -p; Write each file; packing and YAML per skills/rr-builder/rr-test-endless/refs/work-pack-sizing.md).

Final chat message only per orchestration-core.md Callback contracts (Planner).

PLUGIN_ROOT=<absolute>
REPO_ROOT=<absolute>
```

**Callback:** **`orchestration-core.md`** § Callback contracts (Planner).

---

## Execute

**Subagent:** **`test-endless-fix`** — **`STAGE=fix`**; receives **`plan_path`** + **`branch_name`**, owns worktree lifecycle. **No `EVAL` required.**

**Callback:** **`orchestration-core.md`** § Callback contracts (Worker).

**Prompt skeleton:**

```text
STAGE=fix
REVIEW_ID=<reviewId>
REVIEW_DIR=.ai/review/<reviewId>

Execute review fix pack. Base branch: <base>.
<base> must be the integration branch (pre-flight current branch), not master or main; the worker refuses protected trunk as merge target.
REPO_ROOT: <absolute path>
PLUGIN_ROOT: <absolute path>
plan_path: <path under REVIEW_DIR/plans/trp-*.md>
branch_name: <YAML branch: from plan frontmatter>

Follow agents/test-endless/fix.md (EVAL=test workflow) in full — test-trim invariant, scoped Phase A per stack refs, Phase B gate timeout per project-detection.md § Worker final gate timeout.

Callback per orchestration-core.md § Callback contracts (Worker).
```

**Strict parsing:** per **`orchestration-core.md`** § Callback contracts (Worker).
