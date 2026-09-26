# Test-endless leaf contract

**Audience:** `test-endless-assess`, `test-endless-plan`, `test-endless-fix`, `test-endless-toolchain`, and the depth-0 orchestrator when building `Task` prompts.

Every leaf **`Task`** must receive this envelope. Leaves **do not choose the rubric** — the orchestrator sets **`EVAL`** and/or **`LOAD`**.

## Required fields

| Field | Required | Role |
|-------|----------|------|
| **`STAGE`** | yes | `assess` \| `plan` \| `fix` \| `toolchain` — must match the dispatched agent |
| **`EVAL`** | assess* | `test` for assess Tasks |
| **`LOAD`** | optional | Plugin-relative paths to `Read`; wins over defaults when present |
| **`FILES`** | assess* | Review target (newline list or **`CHUNK_SCOPE`**) |
| **`ASSESSMENT_PATHS`** | plan | Newline list of assess artifact paths for this round |
| **`REVIEW_ID`** | yes | Run id: `yyyymmdd-NN` per `artifacts.md` |
| **`REVIEW_DIR`** | yes | `.ai/review/<REVIEW_ID>/` (repo-relative) |
| **`PLUGIN_ROOT`** | yes | Installed **rrraw** plugin root |
| **`REPO_ROOT`** | yes | Repository under review (absolute) |

\*Assess requires **`EVAL=test`** and scope. Plan requires **`ASSESSMENT_PATHS`**.

Optional: **`CHUNK_SCOPE`** / **`chunk_id`**, **`BRIEF_PATH`**, **`MERGE_BASE`**, **`Scope:`** narrative.

## Agent ↔ stage

| `STAGE` | `subagent_type` | Agent file |
|---------|-----------------|------------|
| `assess` | `test-endless-assess` | `agents/test-endless/assess.md` |
| `plan` | `test-endless-plan` | `agents/test-endless/plan.md` |
| `fix` | `test-endless-fix` | `agents/test-endless/fix.md` |
| `toolchain` | `test-endless-toolchain` | `agents/test-endless/toolchain.md` |

**`STAGE` mismatch** → **stop:** `STAGE mismatch`.

## Disk writes

- All persisted markdown for this run lives under **`REVIEW_DIR`** per **`artifacts.md`**.
- Leaves **must not** mint a second run id or write under legacy `.ai/t/` trees.
- **Assess:** markdown under **`REVIEW_DIR/test/assess/tra-*.md`** per **`assess-output.md`**.

## Callbacks

**Assessor:** one **`Report written: <path>`** line per artifact (under **`REVIEW_DIR`**).

**Planner:** **`Plan written: <path>`** or **`Plans written:`** + bullet list (paths under **`REVIEW_DIR/plans/`**).

**Worker:** entire final message = JSON only: `{ "success": true }` or `{ "success": false, "error": "..." }`.

**Toolchain:** structured summary per `agents/test-endless/toolchain.md` — build/test phase pass or fail.

## Stop conditions

- Missing **`REVIEW_DIR`** → stop; do not invent paths
- Assess agent: **no Edit** of application/test source (report-only)
- Required **`Read`** fails → stop; report exact path
