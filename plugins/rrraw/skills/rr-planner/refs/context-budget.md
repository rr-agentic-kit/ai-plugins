# context-budget

**Owner:** Token budget for Plan standing/PRD/delta docs — detect (script + dual-runtime hooks + skill gate) and optimize (`--optimize`). SoT for thresholds, inject contract, scoped load, and naming migrate hints.

**Load when:** End of `standing`; before research/challenge `Task`; resume when standing dirty; `--optimize`; ambient plugin hooks when installed.

**Does not:** Guess size by characters/`wc`. Does not inject file bodies. Does not auto-rewrite on hard. Does not own Discover stem budgets.

## Thresholds (tiktoken)

| Signal | Rule |
|--------|------|
| Soft | file ≥ **5_000** tokens → attention; offer `--optimize` |
| Hard | file ≥ **8_000** tokens → attention + skill may block full-load strategy |
| Encoding | `cl100k_base` via **tiktoken** (budget unit; not model-exact) |
| Measure | `scripts/context_budget.sh` only — skill/hook must not guess chars |

## Script

| Piece | Path |
|-------|------|
| CLI | `scripts/context_budget.sh` → `context_budget_script` |
| Modes | `--file <path>` (single); `--plan-dir <dir>` (all plan `.md` + linked); `--hook --runtime cursor\|claude` (adapter) |
| Output | JSON `{files:[{path,tokens,tier: ok\|soft\|hard}]}` — **no bodies** |
| Exit | `0` if no `hard`; `1` if any `hard` (skill gating); hook adapter always fail-open on infra |

Marketplace runners: monorepo `uv sync` installs `tiktoken`; plugin shell resolves CPython 3.14+ / `uv run --with tiktoken` when needed.

## Dual-runtime plugin hooks

Ambient detect when the **rrraw** plugin is installed (Cursor + Claude). Shared adapter + dual manifests — see monorepo `.agents/hooks.md`.

| Intent | Cursor | Claude |
|--------|--------|--------|
| Grow-on-write | `afterFileEdit` → `--file` | `PostToolUse` `Edit\|Write` → `--file` |
| Entry scan | `beforeSubmitPrompt` if prompt mentions `rr-planner` → `--plan-dir` | `UserPromptSubmit` same gate |
| Unused | `sessionStart` | `SessionStart` |

| Artifact | Role |
|----------|------|
| `hooks/hooks.json` | Claude discovery |
| `hooks/cursor.json` | Cursor (`plugin.json` `"hooks"`) |
| `hooks/context_budget_hook.sh --runtime cursor\|claude` | Thin launcher → `context_budget.sh --hook` |
| `scripts/context_budget_script/hook.py` | Filter path/prompt + emit inject JSON |

**Inject:** receipts only (path / tokens / tier / `--optimize` hint). Cursor: `additional_context` / `agent_message`. Claude: `hookSpecificOutput.additionalContext`. Silent when under budget or filter miss. Fail-open if tiktoken/script missing.

Editing a plan doc is the grow-on-write signal — no `rr-planner` string required. Entry scan requires `rr-planner` / `/rr-planner` in the prompt (case-insensitive).

## Skill detect (cascade)

After `standing` mint/humanize; before research/challenge `Task`; on resume when standing dirty:

1. Run `sh scripts/context_budget.sh --plan-dir {output_dir}` (or `--file` for one dirty path).
2. Structural smells under budget → link spine-test / challenge-method; no prose duplication here.
3. Soft → surface attention + Next Up `--optimize`; continue.
4. Hard → **do not** auto-rewrite; block full-load strategy; emit `CONTEXT_BUDGET_EXCEEDED`; Next Up `--optimize`. Scoped load only (below).

Skill detect remains authoritative for Plan cascade gates even when hooks are absent.

## `--optimize` (manual side path)

**Flag:** `--optimize` → `payload.action: optimize`  
**NL:** “optimize plan docs”, “context budget”, “split architecture”, rename constitution migrate, etc.

**Scope:** all plan documents under `output_dir` **plus** linked docs the script resolves.

**Procedure (suggest → AskQuestion → apply):**

1. Run script → list soft/hard + structural smell pass.
2. For each problem file, propose **1–3 alternatives** (compress / merge duplicates / split to constitution index + on-demand shards / refile product mechanism → `deltas/` / rename architecture→constitution migrate / `adr-lite`→decision-lite wording).
3. AskQuestion — user picks alternative(s) or abort. **No silent path rewrite.**
4. Apply chosen edits → `compose-prose` humanize → dirty challenge attestation → re-run script.
5. Loop ≤2 then stop + manual triage.

## Progressive disclosure (post-optimize target)

```
docs/rr/{track}/plan/
  constitution.md                 # ALWAYS-LOAD: brief + invariant INDEX
  constitution/invariants/        # ON-DEMAND: full decision-lite bodies (optional)
  architecture.md or adrs/        # TECH ADRs only (on-demand)
  deltas/<feature-id>.md          # product-delta / decision-lite (on-demand)
  prd.md                          # phase-scoped load
```

Pins: dual-read `architecture_rev` during transition; prefer `constitution_rev` once standards land.

## Scoped load contracts

| Phase | Load |
|-------|------|
| `dual-lens` | constitution index + that feature’s delta (+ cited tech ADR only) |
| `research` | **no** “read all”; brief/sections in scope + constitution index + load-bearing deltas |
| `challenge` | one target; supporting = index + named contradiction candidates |
| `slice-freeze` | existing `delta_paths` + constitution/tech pins as needed |

Hard exceed → refuse corpus dump; use scoped load or `--optimize` first.

## Naming (standing model)

| Role | Path / id |
|------|-----------|
| Standing always-load law | `constitution.md` (brief + Bind/Prevent/Rule INDEX) |
| Tech ADRs only | `architecture.md` / `adrs/` — `ADR-n` |
| Product feature-delta | `deltas/<feature-id>.md` — decision-lite; `DEC-n` or feature-scoped revs — **not** `ADR-*` |
| Shared record shape | `refs/decision-lite.md` (was adr-lite) |

Standards: [doc-standards/constitution.md](doc-standards/constitution.md), [doc-standards/architecture.md](doc-standards/architecture.md), [decision-lite.md](decision-lite.md).

## Done-when

- Soft/hard detected via script (not char guess)
- Hooks inject receipts only when soft/hard; silent otherwise
- Hard blocks full-load; `--optimize` is suggest→AskQuestion→apply
- Scoped load respected for research/challenge/dual-lens
