# Project design — init-like explore

Use during **design** when `scope=project`.

## Goal

Ground project `CLAUDE.md` in **actual** repo facts—not generic placeholders.

## Explore (before drafting sections 2–6)

1. Read `README`, `package.json` / `pom.xml` / `pyproject.toml` / `go.mod` as present.
2. Skim top-level dirs (`src`, `apps`, `services`) for layout.
3. Find test/lint scripts (Makefile, `package.json` scripts, `./mvnw`, `uv run pytest`, etc.).
4. Note existing agent files: `AGENTS.md`, parallel agent instruction files (path-scoped rules dirs), `CLAUDE.md` fragments.

Prefer a **Task** subagent with `subagent_type=explore` when the tree is large; return stack, commands, and architecture bullets only.

## Stop

Do not invent versions or commands not found—use “(confirm with user)” placeholders and AskQuestion.

## After explore

Draft per `project-sections-template.md`; merge user prompt constraints.
