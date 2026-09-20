# Command design

Judgment for slash **commands**. Shared principles: `design/design-core.md`. Field tables: `frontmatter-schemas.md`. Orchestration facts: `chat-orchestration.md`.

## Role

Commands are the **user slash contract**: inputs, delegation to a skill **Action**, output shape. They are not progressive-disclosure packs and must not leak `refs/` or `plugins/` paths into the user-facing body.

## Access economy (commands)

1. Always emit portable minimum: `name` + `description` + Action body (Input / Execution / Output).
2. Add `argument-hint` when the slash expects args (`$ARGUMENTS` / `$0` patterns in body when args exist).
3. Add Claude `allowed-tools` only for side-effect narrowing / pre-approve—not a substitute for skill Action ownership.
4. Optional Claude `model` only when the command must pin a model; prefer omit in marketplace defaults.

## Action delegation

| Do | Do not |
|----|--------|
| `Execute **Action: …** in skill **id**` | Chain other slashes as the **only** execution path |
| Let the skill Action own Load + procedure | List `refs/actions/...` or `plugins/...` in the command body |
| Pin output shape (fields / write-stop) | Free-form “report something useful” |

Platform fact: Cursor plugin commands cannot chain—slash names in bodies are user homework only (`chat-orchestration.md`).

## When to set frontmatter extras

| Field | Set when | Skip when |
|-------|----------|-----------|
| `argument-hint` | Slash takes args or flags | No inputs beyond empty invoke |
| `allowed-tools` (Claude) | Command body implies side effects that need turn grants | Skill Action already owns all tools; Cursor-only target |
| `model` (Claude) | Product requires a specific model | Marketplace default / inherit is fine |

## Body contracts

- **Input contract** — REQUIRED inputs; behavior when missing (ask once, stop).
- **Execution** — Action delegation only; Progress / TodoWrite when the action has step ids.
- **Output** — Fixed sections or template; stdout-friendly when pipeable.
- **Side-effects** — State whether file edits are allowed or forbidden.
- **Delivery channels** — If body uses AskQuestion / enumerable gates: prefer AskQuestion + text-mode same options; else one-line N/A.

## Anti-patterns

| Anti-pattern | Why it fails |
|--------------|--------------|
| Internal `refs/` / `plugins/` paths in body | Leaks layout; skill Action owns Load |
| Slash-chain-only routing | Commands cannot execute other commands |
| Missing output shape | Unverifiable success |
| `allowed-tools` without Action ownership | Frontmatter grant ≠ procedure |
| No `argument-hint` when args are expected | Discovery miss on Claude slash UX |
