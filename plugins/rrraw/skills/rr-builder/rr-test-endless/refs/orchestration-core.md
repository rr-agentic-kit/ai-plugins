# Test-review orchestration core (shared)

**Audience:** **`rr-test-endless`** orchestrator (depth 0). **Load first** before lane-specific loop sections.

> **Disk contract:** **`REVIEW_DIR/plans/trp-*.md`** is the sole source of truth for work order and execution progress (**`[executed]`** / **`[verified]`** on step lines). **`REVIEW_DIR/test/assess/`** holds assessment facts. **`REVIEW_DIR/test/state/`** is optional — never overrides plan files. Checkpoint JSON schema: **`artifacts.md`** (single SoT).

**Why:** Nested **`Task`** is unavailable in many hosts. The **command** owns the loop and invokes **`Task`** only for **leaf** agents: **`test-endless-assess`**, **`test-endless-plan`** (no **`EVAL`**; assessment path list), **`test-endless-fix`** (**`plan_path`**), and **`test-endless-toolchain`**.

**Orchestrator role (shared):** Do **not** edit application or test code yourself — only **`Task`** to leaf agents above, plus **Read** refs, **optional** **`Write`** under **`REVIEW_DIR/test/state/`** (not execution queue state). **Dispatch and progress** live on **plan markdown**; merge assessment markdown (**`COUNTS:`** + tables) in the command session.

---

## Nomenclature (canonical)

| Term | Meaning |
|------|---------|
| **Step** | One checkbox line under **`## Steps`** in a plan file — the execution unit. |
| **Assess-group** | **Assess-time** scope: one **chunk** from **chunking.md** — **`chunk_id`** + **CHUNK_SCOPE** path prefixes. Fan-out of assess/plan **`Task`**s is per assess-group. |
| **Work-pack** | **One** worker **`Task`** = **one** planner-written **`REVIEW_DIR/plans/trp-*.md`** file (default). Packs per **`skills/rr-builder/rr-test-endless/refs/work-pack-sizing.md`**. |
| **Plan file** | **One** **`REVIEW_DIR/plans/trp-*.md`**. The planner emits **one or more** per **round** (not per chunk). |

Refs may still say **`chunk` / `chunk_id`** — treat as **assess-group** in prose.

---

## Scope from prompt

- **Default:** branch diff (merge-base to `HEAD`) when the command resolved scope that way.
- **Overrides:** explicit **`Scope:`** line from the command (entire codebase, paths, etc.).

All **`Task`** prompts must include **`REPO_ROOT`**, **`REVIEW_ID`**, **`REVIEW_DIR`**, **`Scope:`** / chunk scope as applicable, optional **`BRIEF_PATH`** on assess/re-assess, and **`PLUGIN_ROOT=`** so subagents can **Read** plugin paths. See **`skills/rr-builder/rr-test-endless/refs/leaf-contract.md`**.

---

## Pre-flight

Run from **`REPO_ROOT`** (use **Shell** / **Glob** as needed).

1. **`<base>` (integration branch — never trunk):**
   - **Compute:** **`git branch --show-current`** at pre-flight → that local branch name is **`<base>`** for the whole loop (passed to every worker **`Task`** as **“Base branch: `<base>`”**). **No** **`$ARGUMENTS`** override unless a lane command explicitly documents one.
   - **If `<base>` is `main` or `master` (ASCII case-insensitive):** **hard stop** — emit **Stopped:** **`policy`** per **`terminal-report.md`** / **`exit-conditions.md`**: operator must **`git checkout <integration-branch>`** first, then re-run. The worker **refuses** **`master`**/**`main`** as **`<base>`** (see **`agents/test-endless/fix.md`** **Base policy gate**).
   - **If not on trunk:** **`<base>`** = that branch. Optional disposable branch for **your** working checkout only: create it **from `<base>`** if you need isolation, but **`<base>`** passed to workers **remains** the integration branch — **never** `main`/`master`.
2. **Project detection:** Per **`skills/rr-builder/rr-test-endless/refs/project-detection.md`**. If **no test framework** → hard stop.
3. **Chunk list:** Build **`chunk_id`** list per **`skills/rr-builder/rr-review/refs/chunking.md`** for this scope. Same repo snapshot → same chunks (deterministic). **Skip when `Start: execute`** and checkpoint provides **`assessment_paths_by_chunk`** (§4 queues from **`Glob`**; no assess runs) — do not **Read** `chunking.md` for that run.
4. **Size:** Classify per **size-thresholds.md** for logging; chunking bounds each assess **`Task`** scope.

---

## Callback contracts (strict)

**Canonical source** for assessor, planner, and worker return shapes. **`prompts.md`**, **`orchestration.md`**, and leaf agents **point here** — do not duplicate callback prose elsewhere.

**Assessor (`test-endless-assess`, `STAGE=assess`, `EVAL=test` or bundled list)** — orchestrator mode:

1. Subagent’s **final chat line(s)** are **file reference(s)** only: one **`Report written: <path>`** per assess artifact (repo-relative or absolute under **`REPO_ROOT`**; must be under **`REVIEW_DIR`**). When the parent bundled multiple lanes on one chunk, expect **multiple** lines in **`EVAL`** list order.
2. **Read** each path; each **file body** is **markdown** per **`assess-output.md`** (test) or the lane’s output ref. **Do not** `JSON.parse` assessment files.
3. **Parse** the **`COUNTS:`** line for **`MISSING`**, **`NON-COMPLIANT`**, **`OVER-TESTED`**, **`UNCLEAR`**, **`ADEQUATE`** integers. Extract **markdown table** body rows for planner input / logging.
4. On missing **`COUNTS:`** or unparseable counts → **one** retry of the assess **`Task`** with instruction: required **`COUNTS:`** line + markdown table per **`assess-output.md`**.
5. Second failure → **hard stop** for that chunk → **Report**.

**Planner (`test-endless-plan`, `STAGE=plan`)**:

1. Subagent’s **final chat message** is **file-reference only** (no JSON):
   - **One plan file:** single line **`Plan written: <repo-relative path>`**
   - **Multiple plan files (one chunk):** first line **`Plans written:`**, then a **markdown bullet list** of repo-relative paths (one `- path` per line).
2. **Parse** all **`plan_path`** values from that message. **Read** each plan markdown. **`branch_name`** from YAML **`branch:`** (required). Worker runs **all** steps under **`## Steps`**. **Do not** re-pack in the runner. No **`JSON.parse`** on chat.
3. **Optional sanity check:** If multiple paths were announced but any file is missing **`pack_sequence`** / **`sequential_after`** in YAML where required per **`skills/rr-builder/rr-test-endless/refs/work-pack-sizing.md`**, **stop** and **Report** — do not invent packing in the runner.

**Worker (`test-endless-fix`, `STAGE=fix`)**:

1. **`JSON.parse`** the subagent’s **entire** final message — **no** fence stripping.
2. On failure → **one** retry: final message = **only** `{ "success": true }` or `{ "success": false, "error": "..." }`.
3. Second failure → **hard stop** for that work-pack batch → **Report**.

---

## Shared load list (plugin root)

Prefix each path with **`PLUGIN_ROOT/`** when **Read**ing. If any **core** file fails to load → stop; report path; emit **Stopped:** per **terminal-report.md**.

### Core bundle (always — before loop)

**Read all 7 in one parallel turn** (co-named peers — do not Read one-per-turn):

1. `skills/rr-builder/rr-test-endless/refs/orchestration-core.md` (this file)
2. `skills/rr-builder/rr-test-endless/refs/orchestration.md`
3. `skills/rr-builder/rr-review/refs/chunking.md` (skip Read when `Start: execute` — Pre-flight §3)
4. `skills/rr-builder/rr-test-endless/refs/project-detection.md`
5. `skills/rr-builder/rr-test-endless/refs/artifacts.md`
6. `skills/rr-builder/rr-test-endless/refs/exit-conditions.md`
7. `skills/rr-builder/rr-test-endless/refs/terminal-report.md`

### Phase bundles (load per **`Start:`** and active loop §)

**Read each bundle's paths in one parallel turn** when that bundle's § becomes active — do not Read one-per-turn.

| Bundle | Paths | Load when |
|--------|-------|-----------|
| **assess** | `refs/phases/assess.md`, `refs/assess-output.md`, `refs/prompts.md`, `refs/leaf-contract.md` | §1, §2, §8; **`Start: plan`** (aggregate only) |
| **plan** | `refs/phases/plan.md`, `refs/work-pack-sizing.md`, `refs/prompts.md` | §3, §3a, §3b |
| **execute** | `refs/phases/execute.md`, `refs/prompts.md`, `refs/fix-worktree.md`, `skills/rr-git/refs/worktree-lifecycle.md` | §4–§6 |
| **verify** | `refs/phases/verify.md`, `refs/phases/coverage.md` (toolchain prompt) | §7; §0 when **`n > 1`** |
| **logging** | `refs/size-thresholds.md` | Pre-flight tier log only |

**Helper CLI** (no Read): `scripts/endless_test_helpers/cli.py` — see **SKILL.md** Helper CLI table.
