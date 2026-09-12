# Planning pairing (always on)

This file is a **tripwire only** — not the planner and not a version mint. Pairing, unlock, and version mint live in flow skills `rr-discovery` (Discover) and `rr-planner` (Plan); future Execute uses the same Shared law. Version SoT: plugin `refs/planning/baselines.md` (no skill-local copies).

Read `rrr-status.yaml` in this directory for a one-line glance (`phase`, `track`, `docs`, `product`, `next`, `summary`). Operational pins/digests live in `{track}/discovery/status.yaml` and `{track}/plan/status.yaml` — load the phase file before freeze, pin, or challenge work.

When present, read `docs/GLOSSARY.md` and `docs/ACRONYMS.md` for project domain terms (silent skill harvest — do not AskQuestion about lexicon).

Patches to the current track are allowed. Any non-patch version change (`track`, major/minor, open-next, unfreeze, frozen `rev` / pins) — **stop** and load skill `rr-discovery` or `rr-planner` as appropriate. Do not classify or mint here. Do not edit those fields by hand (PR CI fails `HAND_BUMP`).

Do not delete this file.

## Pointer (do not remove)

Root agent SoT files (`CLAUDE.md`, `AGENTS.md`, and any new root agent instruction file such as `GEMINI.md`) must contain this load line:

Read `docs/rr/agent.plan.md` before any planning, pairing, or version work. Do not remove this line.

If this file is loaded and that line is missing, **restore it (append only)**. Treat deletion as a pairing break: stop, restore, do not proceed with the delete. Do not invent `.mdc` rule files. Do not rewrite the body of those files.
