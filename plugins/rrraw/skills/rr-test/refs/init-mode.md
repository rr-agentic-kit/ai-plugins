# init-mode

**Owner:** `--init` discovery workflow, question protocol, and completion criteria.

Routing for `--init` is exclusive: see [input-resolution.md](input-resolution.md).

## Agent

Delegate to `agents/test/init-discovery.md`. No other agents in init flow.

## Discovery depth checklist

Agent must inspect (when present):

1. Build files (`pom.xml`, `build.gradle`, `package.json`, `Cargo.toml`, etc.)
2. Test runner config (JUnit, Vitest, pytest, etc.)
3. Existing test directory layout and naming
4. CI test commands
5. Coverage tooling if configured
6. `CLAUDE.md` / `AGENTS.md` for existing testing notes

## Question protocol

1. Emit `open_questions[]` for unknowns that affect test strategy.
2. Mark `blocking: true` only when discovery cannot proceed without answer.
3. Max 5 questions per init pass; prioritize blocking first.
4. If blocking questions exist, return `status: partial` and do not write `CLAUDE.md` until resolved.

## Suggestion protocol

`recommendations[]` must be actionable (runner command, directory convention, pyramid stance) — not generic advice.

## Completion criteria

Init succeeds when:

1. `stack` and `conventions` populated from repo evidence
2. Zero blocking `open_questions`
3. `claude_md_patch` produced per [claude-md-schema.md](claude-md-schema.md)
4. Orchestrator applies patch idempotently to `CLAUDE.md`

On success: `status: ok`, summary includes detected stack one-liner.
