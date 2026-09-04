# agent-config

**Owner:** Injection version, the one load line on root agent SoT files, and the `agent.plan.md` body. Skill is the only writer of `docs/agent.plan.md` and of that one line on root SoT files.

**Load when:** Every resolve (sync); first compose (emit + sync); `--setup`; when `rrr-status.yaml.claude_config_version` lags `injection.version`.

Pairing policy lives in [baselines.md](baselines.md). This file locks wording so the skill and `validate_planning.sh --sync-agent-config` / `--setup` stay identical.

## Injection (machine-readable)

```yaml
injection:
  version: 1
  load_line: "Read `docs/agent.plan.md` before any planning, pairing, or version work. Do not remove this line."
```

Exact `load_line`. Append only. Never rewrite the rest of `CLAUDE.md` / `AGENTS.md` / other root SoT files. Do not invent `.mdc` rule files.

## Root SoT sync

Known today: `CLAUDE.md`, `AGENTS.md` at repo root **if the file exists**. Also any new root file that is clearly an agent source of truth: `GEMINI.md`, `CODEX.md`, `CURSOR.md`.

| Case | Action |
|------|--------|
| File exists, line missing | Append the load line. |
| File exists, line present | No-op (idempotent). |
| File absent | Do **not** create it. A one-line file is allowed only when that tool’s SoT is already the project’s convention (the user or tool added the file). |
| Line deleted | Restore (append). Same class as a pairing violation — stop, restore, do not proceed with the delete. |
| New root SoT appears | Add the same one line. Do not rewrite the body. |

When `injection.version` advances: refresh `agent.plan.md` from [agent.plan.md](agent.plan.md), re-sync every existing root SoT, set `rrr-status.yaml.claude_config_version` to this version.

Skill invokes (plugin root):

```bash
sh scripts/validate_planning.sh --sync-agent-config --repo-root <PROJECT_ROOT> <phase-dir>
# or: --sync-agent-config --repo-root <PROJECT_ROOT> --docs-root <PROJECT_ROOT>/docs
```

`<phase-dir>` is `docs/discovery/` or `docs/plan/` (sync resolves the parent `docs/` for `agent.plan.md` + `rrr-status.yaml`). First compose uses the same command after writing phase status. `--setup` runs the same writes as part of its section list ([setup.md](setup.md)).

## agent.plan.md template

Body source is sibling [`agent.plan.md`](agent.plan.md). Exact bytes written to `{PROJECT_ROOT}/docs/agent.plan.md`. Overwrite the project file when `injection.version` advances. Skill-owned. Not validator cascade input.
