# Dual-runtime plugin hooks

Committed monorepo cheat sheet for marketplace plugins that ship hooks on **both** Cursor and Claude Code. Personal overrides stay in gitignored `.agents/local.md`.

## Why dual manifests

Claude Code discovers `hooks/hooks.json` by default. Cursor uses a different schema (`version: 1`, different event names) and loads the path declared in `.cursor-plugin/plugin.json` → `"hooks": "./hooks/cursor.json"`.

Do **not** point Cursor at Claude’s `hooks.json` — schemas collide (`version` / event names / matcher shape). Ship:

| Artifact | Runtime |
|----------|---------|
| `plugins/<name>/hooks/hooks.json` | Claude Code (default discovery) |
| `plugins/<name>/hooks/cursor.json` | Cursor (via plugin.json `"hooks"`) |
| `plugins/<name>/hooks/<adapter>.sh` | Shared adapter (`--runtime cursor\|claude`) |
| Shared CLI under `scripts/` | Tokenize / business logic |

## Event map

| Intent | Cursor | Claude Code |
|--------|--------|-------------|
| Grow-on-write | `afterFileEdit` | `PostToolUse` matcher `Edit\|Write` |
| Prompt-gated entry | `beforeSubmitPrompt` | `UserPromptSubmit` |
| Tool evidence accumulate | `postToolUse` / `postToolUseFailure` | `PostToolUse` / `PostToolUseFailure` |
| Keep session + inject follow-up | `stop` (`followup_message`; `loop_limit`) | `Stop` (`decision: "block"` + `reason` / `additionalContext`; check `stop_hook_active`) |
| Scratch cleanup only (no inject) | `sessionEnd` | `SessionEnd` |
| Not used for first-prompt detect | `sessionStart` | `SessionStart` |

`SessionStart` / `sessionStart` cannot read the first user message — keep them out of prompt-gated scans.

**Stop vs SessionEnd:** SessionEnd is fire-and-forget / cleanup-only on both hosts (response ignored or discarded; cannot block termination). The mechanism that continues the chat for auto-learn is **`stop` / `Stop`**. Do not “fix” inject back onto SessionEnd.

## Inject fields

| Runtime | Soft/hard attention inject | Cap |
|---------|----------------------------|-----|
| Cursor | Top-level `additional_context` and/or `agent_message` | ~10k chars |
| Cursor `stop` | Top-level `followup_message` (auto-submits next user turn) | lean ~2k for auto-learn |
| Claude | `hookSpecificOutput.additionalContext` (+ `hookEventName`) | ~10k chars |
| Claude `Stop` | `decision: "block"` + `reason` (and/or `additionalContext`) | lean ~2k for auto-learn |

Budget / attention hooks: inject **receipts only** (`path`, `tokens`, `tier`, needs attention / `--optimize`). **Never** inject file bodies.

Auto-learn Stop inject: lean instruction only (bound skill, absorb-into, signal ids + one evidence line each, `--auto-learn` verb). Mark session evidence **consumed** so a second Stop does not re-fire.

Cursor event support for inject fields evolves — prefer fail-open when the host ignores unknown output keys. When grow-on-write inject is unreliable on `afterFileEdit`, document the gap in the plugin README (dual-runtime parity rule).

## Paths

| Runtime | Plugin root |
|---------|-------------|
| Claude | `${CLAUDE_PLUGIN_ROOT}` — absolute-ish via env |
| Cursor | Relative from plugin root: `./hooks/...` |

## Fail-open

| Case | Behavior |
|------|----------|
| Missing Python / tiktoken / script | Exit `0`, no stdout — silent |
| Path / prompt outside filter | Exit `0`, silent |
| Soft/hard findings | Exit `0` + JSON inject (hooks never block the edit/prompt for budget) |
| Infra errors in adapter | Exit `0` — fail-open |

Exit `2` semantics differ by event and host (often “block”); budget hooks must not use exit `2` for soft/hard attention.

Skill cascade gating (non-zero CLI exit on any `hard`) is separate from the hook adapter — hooks wrap the CLI and always fail-open on infra.

## Pattern

1. One shared CLI package (`scripts/<name>.sh` → `python -m <package>`).
2. Thin `--runtime cursor|claude` shell: resolve CLI path, forward stdin, fail-open (`|| exit 0`). No business logic in the shell.
3. Adapter logic lives in the Python package (e.g. `context_budget_script.hook`): parse host JSON → filter path/prompt → **in-process** measure → emit **runtime-correct** inject JSON. Entry: `--hook --runtime …`.
4. Tests under `tests/<plugin>/` unit-test the Python adapter; keep at most one shell smoke for fail-open.

## Project vs plugin hooks

| Location | Role |
|----------|------|
| Monorepo `.cursor/hooks.json` | Repo-local (e.g. black) — not shipped |
| `plugins/<name>/hooks/` | Marketplace install artifact |

## Docs pointers

- Cursor hooks: https://cursor.com/docs/hooks
- Claude Code hooks: https://code.claude.com/docs/en/hooks
- First dual example: `plugins/rrraw` context-budget (`hooks/` + `scripts/context_budget.sh` → `context_budget_script.hook` + `skills/rr-planner/refs/context-budget.md`)
- Auto-learn drift: `plugins/context-eng-hero` (`hooks/` + `scripts/auto_learn.sh` → `auto_learn_script` + skill `--auto-learn`)
