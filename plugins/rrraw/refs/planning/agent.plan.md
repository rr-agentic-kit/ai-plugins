# Planning pairing (always on)

This file is not the planner. Pairing, unlock, and version mint live in skills `rr-discovery` (Discover: executive-summary → BRD + business-case) and `rr-planner` (Plan: PRD+ from frozen business case).

Read `rrr-status.yaml` in this directory for a one-line glance (`phase`, `track`, `summary`). Operational pins/digests live in `discovery/status.yaml` and `plan/status.yaml` — load the phase file before freeze, pin, or challenge work.

Patches to the current track are allowed. Any non-patch version change (`track`, major/minor, open-next, unfreeze, frozen `rev` / pins) — **stop** and load skill `rr-discovery` or `rr-planner` as appropriate. Do not classify or mint here. Do not edit those fields by hand.

Do not delete this file.

## Pointer (do not remove)

Root agent SoT files (`CLAUDE.md`, `AGENTS.md`, and any new root agent instruction file such as `GEMINI.md`) must contain this load line:

Read `docs/agent.plan.md` before any planning, pairing, or version work. Do not remove this line.

If this file is loaded and that line is missing, **restore it (append only)**. Treat deletion as a pairing break: stop, restore, do not proceed with the delete. Do not invent `.mdc` rule files. Do not rewrite the body of those files.
