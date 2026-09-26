# Helper CLI (scripts executed, not loaded)

When a skill folder includes `scripts/`, the agent **runs** them via shell—it does **not** load script source into context as documentation.

Load with **create**, **fix**, **design**, and **audit** when the target skill has `scripts/` **or** the case is a deterministic fetch/filter/id-keyed write that should become a script (see **When to add `scripts/`**).

## Core rule

| Do | Do not |
|----|--------|
| Document **invoke line**, args, stdout shape, exit codes in SKILL or a short `scripts/README.md` | Paste full Python/bash into SKILL body |
| Point Procedure to `python3 scripts/<tool>.py …` or `allowed-tools: Bash(…)` | Treat scripts as progressive-disclosure refs to Read |
| One envelope on stdout when output is machine-parsed | Multi-step shell chains the agent reinvents every turn |

Anthropic agent-skills guidance: scripts are **executed**, not loaded as docs.

## When to add `scripts/`

- A user case that is the **same fetch, filter, or id-keyed write every time** — the agent would re-type the chain or dump raw API payloads into context
- Stdout must be **only the fields the next step needs** (ids, filtered rows, stable envelopes) — not URLs, full GraphQL objects, or lists the agent re-filters in chat
- Shell (`#!/bin/sh` + `gh`/`jq`/thin glue) is enough; no general SDK layer required
- Repeatable multi-step workflow where the agent would otherwise invent the same shell chain every turn
- Deterministic structure checks (see plugin `scripts/audit_static.py` as reference)
- Fat CLI that polls internally so the agent waits one invocation
- **Report scaffolding + severity math** from lean JSON (see **Lean emit + schema + render** below; CE exemplar `scripts/render_ce_report.py`)

**Not for:** general SDK layers; one-off prose-only guidance with no repeated invent/dump waste. A **single** documented `git`/`gh` one-liner is fine when it is not reinvented every run — when the miss is unfiltered payloads or missing id-keyed writes, add the script instead of more markdown.

### Improve helpers (plugin root)

| Invoke | Role |
|--------|------|
| `python3 scripts/audit_static.py . <rel>` | Static gate |
| `python3 scripts/render_ce_report.py <kind> --in <json> --out <md>` | Validate lean JSON against `templates/reports/<kind>.schema.json`, Jinja-render markdown; agent must not Write full bodies. Exit **2** = schema/JSON error **or** smashed markdown tables (fix JSON/j2, re-run). |
| `.ai/learning/ce-improve/<run-id>/touch-list.txt` | After Write-gate Approve promote — inventory of promoted paths for close narrative only; **never** `git add` |

## Lean emit + schema + render

Reusable recipe for **targets** (and CE’s own `--improve` path). Compact copy agents can point at without loading Jinja: `templates/reports/README.md`.

**Trigger:** agent would otherwise paste large report/scaffold markdown, reinvent severity/table math, or re-emit the same report shape every turn (**SCRIPTABLE** waste in `improvement-patterns.md`).

**Contract**

| Role | Does |
|------|------|
| Task / subagent | Emits **lean JSON** only (+ one-line status) |
| `refs/templates/reports/<kind>.schema.json` | Output contract — agents **Read** this only |
| Parent / thin `scripts/render_*.py` | Validate with jsonschema → Jinja-render human markdown |
| `*.md.j2` | Scaffolding SoT — **never** load into agent context as docs |

**Target layout**

```text
skills/<target>/refs/templates/reports/<kind>.schema.json
skills/<target>/refs/templates/reports/<kind>.md.j2
skills/<target>/scripts/render_<domain>.py   # or shared plugin helper when appropriate
```

Document invoke + exit **2** = fix JSON in the skill Procedure (and `allowed-tools: Bash(python3 scripts/render_…*)` when Claude turn grants are needed). Prefer this absorb over “add more prose procedure” when ranking **SCRIPTABLE** report waste under create / fix / redesign / improve.

**CE kinds:** `compliance`, `opportunity`, `apply-plan`, `reflection` — schemas under `templates/reports/`.

## Design goals

1. **One agent shell call per workflow step** — collapse chains into one entry point.
2. **Stable stdout** — JSON envelope or fixed columns when the agent branches on output; stderr for human progress only.
3. **Domain logic in Python** — state machines, poll loops, preflight, schema validate + render; thin transport.
4. **Fixture-driven tests** — when tests exist in monorepo; installed plugin may ship without pytest (see plugin root `CLAUDE.md`).

## SKILL authoring pattern

```markdown
## Procedure

1. From plugin root, run `python3 scripts/my_tool.py <args>` (see `scripts/README.md`).
2. Parse stdout; on non-zero exit, stop and report stderr tail.
```

Optional frontmatter:

```yaml
allowed-tools: Bash(python3 scripts/my_tool.py*)
```

## Skill + Ref progressive disclosure

- **SKILL.md** — invariant procedure + when to run which script.
- **`refs/<variant>.md`** — variant flags or output interpretation—linked **one hop** from SKILL **Progressive disclosure**; ref does not link to further refs.
- **`scripts/`** — implementation; README lists subcommands only.
- **Lean report kinds** — agents Read `*.schema.json`; execute render script; never Read `*.md.j2` / script source as docs.

## Forcing test

“Does this reduce agent shell calls, tokens, or duplicated script lines—or only change internal transport?” If only internal transport, keep the existing approach.
