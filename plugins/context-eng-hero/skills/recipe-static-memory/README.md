# recipe-static-memory

Author and repair project or user-global agent instruction packs (`AGENTS.md` and related entry points) so agents stay constrained without becoming a project bible.

## Why

Teams and operators need durable agent contracts—tone, hard rules, commands, tooling triggers—that improve most chats. Those packs fail when they absorb full docs, treat one harness home as the only SoT, or mirror policy into every adapter. This skill designs, reviews, and symptom-fixes instruction packs under a ~90% inclusion bar.

**Done when:** The agreed scope has a lean always-on SoT (project `AGENTS.md` or user `~/.agents/AGENTS.md`), correct thin entry points, optional situational packs or harness overlays only when justified, and disk writes only after confirm-before-write.

## What

- **Scopes:** Project (default) and user-global (opt-in)
- **Project artifacts:** `AGENTS.md`, thin `CLAUDE.md` `@` pointer, optional `.agents/{group}.md` packs
- **User-global artifacts:** Shared SoT `~/.agents/AGENTS.md`; optional `*.specific.md` harness overlays; thin adapters for Claude, Cursor, Codex, Copilot
- **Out of scope:** Plugin skills/commands/rules/workflows (→ `recipe-context-engineer`); enterprise policy paths; auto-sync scripts for adapters

### Verification

Inclusion-bar challenge on design/review/fix; confirm-before-write for memory files; section walk and symptom → layer mapping (no mechanical `audit_static.py` on user home packs).

## Actions

| Action | Outcome | Pick when |
|--------|---------|-----------|
| design | Full draft from scratch (gather → confirm → write) | No file / empty / full rewrite |
| review | Section walkthrough; accept / edit / deep-dive; may delete low-leverage | File exists; systematic audit |
| fix | Symptom-led minimal patch | Agent misbehaved; known path + symptom |

## When

### Use when

- Creating project (default) or user-global instruction packs from scratch
- Walking existing always-on / situational / adapter-overlay files section by section
- Applying a minimal fix when agent behavior diverges from stated prefs

### Avoid when

- Authoring plugin artifacts under `plugins/` (use `recipe-context-engineer`)
- One-off prompts with no durable memory file
- Dumping README/CONTRIBUTING into agent memory “for completeness”
- Ambient home-dir migration without an explicit design/review/fix request

## Philosophy

- **90% inclusion bar** — keep only constraints that help most chats; challenge the rest
- **Pointer over paste** — docs stay authoritative; memory stays the agent contract
- **One shared user SoT** — `~/.agents/AGENTS.md`; harness files are thin adapters + optional overlays
- **Anti-mirror** — never duplicate SoT body into Cursor `.mdc` or other adapters
- **Confirm-before-write** — memory paths are not plugin shared-write-gates

## UX

### Invoke

Slash `/static-memory-*` (Cursor) or `/context-eng-hero:static-memory-*` (Claude); ambient skill use routes only—no user-file write until an action slash.

### Intake

Parse the initial prompt to pre-fill questionnaires; default `scope=project` unless user-global is explicit.

### Clarify

AskQuestion for scope, harness adapters (user), rewrite confirm, section Accept/Edit/Deep-dive/Delete, and write approval.

### Output

Drafts and diff-style summaries in chat; paths + sections/packs/overlays listed on close.

### Close

**Next step (user)** to one slash when ambient; after write, report paths touched—no command chaining.

## Design notes

- **Project layout unchanged** — multi-harness redesign applies to user-global only
- **Partial breaking change** — Claude-only `~/.claude/` packs must migrate SoT to `~/.agents/AGENTS.md`
- **Read force for non-`@` harnesses** — Cursor/Codex/Copilot stubs beat symlinks so overlays stay possible

## Constraints

| Topic | Fact |
|-------|------|
| **Default scope** | `project` unless user names user-global / `~/.agents/` / harness homes |
| **User SoT** | `~/.agents/AGENTS.md` — not `~/.claude/CLAUDE.md` alone |
| **Adapters** | Claude `@`; Cursor alwaysApply `.mdc`; Codex/Copilot Read stubs — no policy body |
| **Overlays** | `~/.agents/{CLAUDE\|CURSOR\|CODEX\|COPILOT}.specific.md` for harness-only prefs |
| **Write gate** | Confirm-before-write in action refs (not CE `shared-write-gates.md`) |
| **First-class harnesses** | Claude Code, Cursor, Codex, Copilot only |
| **Author-to-bar** | Exhaustive comm/role on user design; tooling interview + overlay fork; lean SoT |

## Notes

- Executor: `SKILL.md`. Multi-harness detail: `refs/user-global-multi-harness.md`.
- Plugin commands map: see `SKILL.md` **Plugin commands**.

Executor source of truth: `SKILL.md`. This README is the human spec—not a Procedure echo.
