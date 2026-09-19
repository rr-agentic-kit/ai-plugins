# Project design — init-like explore

Use during **design** when `scope=project` (the default).

## Goal

Ground project `AGENTS.md` in **actual** repo facts—not generic placeholders. Apply the 90% inclusion bar; prefer pointers to README / CONTRIBUTING.

## Explore (before drafting always-on)

1. Read `README`, `package.json` / `pom.xml` / `pyproject.toml` / `go.mod` as present.
2. Skim top-level dirs (`src`, `apps`, `services`, `plugins`) for layout.
3. Find essential test/lint/build entrypoints (Makefile, `package.json` scripts, `./mvnw`, `uv run pytest`, etc.)—not the full quality matrix.
4. Note existing agent files: `AGENTS.md`, `CLAUDE.md`, `.agents/*.md` (flat packs only), path-scoped rules dirs.
5. Identify authoritative docs to **point at** (CONTRIBUTING, ADRs, plugin `CLAUDE.md` / README)—do not absorb.

Prefer a **Task** subagent with `subagent_type=explore` when the tree is large; return stack, essential commands, hard rules, and where-to-look bullets only.

## After explore — split

1. Draft always-on per `project-sections-template.md` (leverage only).
2. Derive situational packs only via `situation-groups.md` (zero packs preferred).
3. Draft thin `CLAUDE.md` with `@AGENTS.md`.
4. Merge user prompt constraints; challenge asks that fail the 90% bar.

## Stop

Do not invent versions or commands not found—use “(confirm with user)” placeholders and AskQuestion.  
Do not invent a fixed `.agents/*.md` catalog.
