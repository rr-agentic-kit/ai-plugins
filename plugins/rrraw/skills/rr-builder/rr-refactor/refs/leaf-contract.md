# Refactor leaf contract

**Purpose:** Define collector Task handoffs consumed by the refactor orchestrator.

**Audience:** `refactor-collector`, command-session inline collect, and the refactor orchestrator when building prompts.

## Collector `Task` envelope

| Field | Required | Role |
|-------|----------|------|
| **`STAGE`** | yes | `assess` — must match collector agent |
| **`REFACTOR_ID`** | yes | Run id (`MM-DD-HH-mm-ss`, collision suffix allowed) |
| **`REFACTOR_DIR`** | yes | `.ai/refactor/<REFACTOR_ID>` (repo-relative) |
| **`EPOCH`** | yes | Current epoch number (integer ≥ 1) |
| **`FILES`** | yes | Newline list of repo-relative paths in scope for this pass |
| **`ASSESS_MODE`** | yes | `full` (all phases 1–8) or `phase` (single phase) |
| **`PHASE`** | when `ASSESS_MODE: phase` | `1`–`8` |
| **`BAND`** | optional | `tool_seed` \| `cohesion` \| `visibility` \| `polish` \| `all` — module Task only |
| **`CHUNK_ID`** | when collector runs as a module/chunk `Task` | Filesystem-safe stable id unique within the epoch |
| **`PLUGIN_ROOT`** | yes | Installed **rrraw** plugin root |
| **`REPO_ROOT`** | yes | Repository under refactor (absolute) |

**Missing required field** → **stop:** `missing <field>`.

## Collector output

Each module/chunk `Task` returns one JSON finding array and does not write files. The orchestrator rejects duplicate `CHUNK_ID` values, writes each response to **`REFACTOR_DIR/epochs/epoch-{NNN}-assess-partial-{CHUNK_ID}.json`**, then merges per **`refs/artifacts.md`** § Partial assess merge.

Task and inline collection outputs are JSON arrays with **every** field in the **`artifacts.md`** finding shape; **`fingerprint`** is mandatory. Only the orchestrator writes partial or merged assess artifacts.

**Forbidden:** skipping mandatory phase packs because tool seeds were empty; writing files; editing production source.

Task error, `error: <reason>`, malformed JSON, or missing expected `CHUNK_ID` dispatch association → retry that chunk once, then **AskQuestion**; do not merge an incomplete assessment.

## Inline fix (command session)

**Does not** use **`Task`** for fix. Execute per **`refs/inline-fix.md`** (sole SoT for verify, rollback, phase order, and manifest updates).

## Callback

Terminal orchestrator chat:

```text
Report written: .ai/refactor/<runId>/report.md
```
