# AI disk artifacts (refactor orchestrator)

**Purpose:** Canonical paths for **rr-refactor** fixed-point runs. **Convention:** paths are at the **repository root** of the project under refactor, not inside the plugin.

**Disk write contract:** The **orchestrator** mints **`runId`** once per run. Every epoch and leaf uses the same **`REFACTOR_DIR`**. **`mkdir -p`** via **`Shell`**, persist with **`Write`**. No heredoc/`echo` **`Shell`** for markdown/JSON bodies.

## Run id

**Format:** `{month-day-hour-minute-second}` = zero-padded local wall clock `MM-DD-HH-mm-ss` (example `08-14-15-20-03`). No year.

**Collision:** If `.ai/refactor/<id>/` exists, append `-2`, `-3`, … — never reuse another run's folder.

### Run id helper (orchestrator step 2)

From **`REPO_ROOT`**, emit a collision-safe id and directory — do not invent ids in prose:

```bash
RUN_ID="$(date +%m-%d-%H-%M-%S)"
BASE=".ai/refactor/${RUN_ID}"
SUFFIX=""
while [ -e "${BASE}${SUFFIX}" ]; do SUFFIX="-$(( ${SUFFIX:-0} + 1 ))"; done
REFACTOR_DIR="${BASE}${SUFFIX}"
mkdir -p "${REFACTOR_DIR}/epochs"
printf '%s\n' "${REFACTOR_DIR#*/}"  # runId stem for REFACTOR_ID
```

Set **`REFACTOR_ID`** to the printed stem; **`REFACTOR_DIR`** to the repo-relative path.

## Module split (>50 files)

When resolved scope exceeds 50 production-source files:

1. Group files by top-level module directory (first path segment under repo root, or `pack-tool-map.md` module key when present).
2. Mint **`CHUNK_ID`** per module: lowercase alphanumeric + hyphen from module key (stable within the epoch).
3. Record module → file list in **`scope.json`** **`modules`** array: `{ "chunk_id", "files" }`.
4. Dispatch one collector **`Task`** per module chunk per **`refs/leaf-contract.md`**.

## Canonical layout

**Root:** `.ai/refactor/{runId}/`

```text
.ai/refactor/{runId}/
  report.md                    # merged terminal report (required at end)
  scope.json                   # initial + expanded scope (required after step scope)
  epochs/
    epoch-001-assess.json      # full-scope assessment (all phases, all in-scope files)
    epoch-001-manifest.json    # execution manifest for epoch 001
    epoch-002-assess.json      # reassess after execute + verify
    epoch-002-manifest.json
    …
  state.json                   # convergence tracker (required after first assess)
```

| Artifact | Path | Required when |
|----------|------|----------------|
| Scope | `scope.json` | After initial scope resolve; update after each scope expansion |
| Assessment | `epochs/epoch-{NNN}-assess.json` | End of every assess step (including confirmation passes) |
| Manifest | `epochs/epoch-{NNN}-manifest.json` | After triage, before execute |
| State | `state.json` | After the first assess; update after every epoch and at terminal status |
| Report | `report.md` | Terminal step |

**Epoch numbering:** `001`, `002`, … zero-padded three digits. One epoch = full-scope assess → triage/manifest → optional execute → verify → scope expansion. Reassessment starts the next epoch.

## scope.json

```json
{
  "runId": "08-14-15-20-03",
  "initial_files": ["src/Foo.java"],
  "expanded_files": ["src/Foo.java", "src/FooHelper.java"],
  "merge_base": "abc123…",
  "scope_mode": "MR | all",
  "modules": []
}
```

- **`expanded_files`** is the authoritative in-scope set for assess/reassess.
- After verification succeeds: union paths from **verified edits**—touched paths, newly created files, and extracted targets—into **`expanded_files`** before the next assess. Exclude rolled-back paths.

## Finding shape (assess + manifest)

Every finding **must** include:

| Field | Required | Notes |
|-------|----------|-------|
| `fingerprint` | yes | Stable id: `{phase}:{file}:{line}:{type}` (normalize paths repo-relative) |
| `file` | yes | Repo-relative path |
| `line` | yes | 1-based; `0` when file-level |
| `phase` | yes | `1`–`8` |
| `type` | yes | e.g. `magic_number`, `god_method`, `visibility` |
| `description` | yes | One-line rationale |
| `disposition` | phase-dependent | `fix` \| `clarify` \| `escalate_human` per collector rules |
| `auto_fixable` | yes | `true` iff the explicit or type-default disposition is `fix`; always `false` for `clarify` / `escalate_human` |

**Auto-fixable closure:** `remaining_fix` = count of findings where `auto_fixable: true` in the latest full-scope assess.

## epoch-{NNN}-assess.json

```json
{
  "epoch": 1,
  "scope_files": ["src/Foo.java"],
  "phases": [1, 2, 3, 4, 5, 6, 7, 8],
  "findings": [],
  "summary": {
    "total": 0,
    "auto_fixable": 0,
    "clarify": 0,
    "escalated": 0,
    "remaining_fix": 0
  },
  "assess_pass": "complete"
}
```

- **`assess_pass: complete`** only after **fresh** collector passes for **all eight phases** on **all** `scope_files` (tools are seeds; mandatory LLM residuals per phase still run).
- Empty tool output does **not** skip phases **4**, **6**, **7** residual, or **8**.

### Partial assess merge

When multi-module **`Task`** collectors return partial JSON arrays, the orchestrator:

1. Writes each response to **`epochs/epoch-{NNN}-assess-partial-{CHUNK_ID}.json`**.
2. Merges all expected chunks deterministically:

```bash
# From REFACTOR_DIR — jq merges finding arrays, sorts by fingerprint, dedupes
jq -s '
  [.[].findings[]?]
  | sort_by(.fingerprint)
  | unique_by(.fingerprint)
' epochs/epoch-*-assess-partial-*.json
```

3. Builds full **`epoch-{NNN}-assess.json`** with merged **`findings`** and recomputed **`summary.remaining_fix`**.

## epoch-{NNN}-manifest.json

```json
{
  "epoch": 1,
  "items": [
    {
      "fingerprint": "1:src/Foo.java:42:magic_number",
      "file": "src/Foo.java",
      "line": 42,
      "phase": 1,
      "type": "magic_number",
      "description": "Literal 42 used without a named constant",
      "status": "pending",
      "disposition": "fix",
      "auto_fixable": true,
      "attempts": 0,
      "reason": null
    }
  ]
}
```

Manifest items carry the complete finding shape plus `status`, `attempts`, and `reason`. `reason` is required when status is `clarified`, `escalated`, or `no_progress`; otherwise it is `null`.

**Status values:** `pending` | `executed` | `verified` | `clarified` | `escalated` | `no_progress`

- Every finding from assess **must** appear. Auto-fixable findings start `pending`; `clarify` / `escalate_human` findings start `clarified` / `escalated` with a reason.
- `no_progress` records the unchanged fingerprint and attempted fix reason for the next epoch.

## state.json

```json
{
  "epoch_cap": 5,
  "current_epoch": 2,
  "consecutive_zero_fix_assessments": 1,
  "last_assess_remaining_fix": 0,
  "status": "in_progress",
  "terminal_reason": null
}
```

## Terminal convergence (SoT)

**`status: complete`** when:

- Expanded scope is **stable** (no new paths added to **`expanded_files`** since the prior assess), **and**
- **`consecutive_zero_fix_assessments` ≥ 2** on full **`expanded_files`** assess passes, **and**
- Latest epoch verify succeeded when execute ran.

**Reset `consecutive_zero_fix_assessments` to `0`** whenever verified edits change **`expanded_files`** — the next assess starts a new clean sequence.

**`status: partial`** when:

- **`epoch_cap`** reached before two consecutive zero-fix assessments (`terminal_reason: epoch_cap_remaining`), **or**
- Latest assess has **`remaining_fix: 0`** but only one consecutive zero-fix pass (`terminal_reason: confirmation_pending`), **or**
- Repeated **`no_progress`** on the same fingerprints across epochs (`terminal_reason: repeated_no_progress`).

**`status: stopped`** when orchestrator aborts after verify failure, user abort via **AskQuestion**, or unrecoverable collector error.

Partial **`terminal_reason`** values: `epoch_cap_remaining` | `confirmation_pending` | `repeated_no_progress`.

## report.md

Header: **Scope**, **Run id**, **Epochs**, **Status**, **Remaining auto-fixable** (count + fingerprints).

When `Status: partial` and `Remaining auto-fixable: 0`, include the terminal reason (for example, `confirmation_pending`).

Sections:

1. **Fixed** — fingerprints resolved this run
2. **Remaining auto-fixable** — only when `partial` or `stopped`
3. **Clarified** — `clarify` dispositions applied
4. **Escalated** — `escalate_human` with short rationale

**Do not** use ambiguous `PASS/FIXED — N` phase lines. Per-epoch tables may list phase × counts; terminal **Status** follows **Terminal convergence** above.

## Task prompt fields

Pass the envelope in **`refs/leaf-contract.md`** on every collector **`Task`**. Chat terminal line: **`Report written: .ai/refactor/<runId>/report.md`**.

## `.gitignore` (consumer repos)

- **Recommended:** ignore **`.ai/refactor/`** or entire **`.ai/`** for local-only AI output.

## Related

- Param grammar: **`refs/params.md`**
- Leaf envelope + inline fix: **`refs/leaf-contract.md`**, **`refs/fix-disposition.md`**, **`refs/inline-fix.md`**
