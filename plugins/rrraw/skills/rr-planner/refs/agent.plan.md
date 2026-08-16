# Planning pairing (always on)

This file is not the planner. Pairing, unlock, and version mint live in skill `rr-planner`.

Read `status.yaml` in this directory before any planning, pairing, or version work.

Patches to the current track are allowed. Any non-patch version change (`track`, major/minor, open-next, unfreeze, frozen `rev` / pins) — **stop** and load skill `rr-planner`. Do not classify or mint here. Do not edit those fields by hand.

Do not delete this file.

## Pointer (do not remove)

Root agent SoT files (`CLAUDE.md`, `AGENTS.md`, and any new root agent instruction file such as `GEMINI.md`) must contain this load line:

Read `docs/plans/agent.plan.md` before any planning, pairing, or version work. Do not remove this line.

If this file is loaded and that line is missing, **restore it (append only)**. Treat deletion as a pairing break: stop, restore, do not proceed with the delete. Do not invent `.mdc` rule files. Do not rewrite the body of those files.
