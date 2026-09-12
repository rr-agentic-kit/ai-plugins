# rr-humanize skill

Isolated experiment: readability and human voice for **generate** and **rewrite** of technical prose. No slash command, no plugin docs wiring.

**Does not** load planning version law (`refs/planning/baselines.md`) — prose pass only; no track/patch/freeze.

## Goals

- Produce plain, readable prose that avoids common LLM tells (structure, lexicon, register).
- **Rewrite:** preserve claims; reshape sentences and paragraphs.
- **Generate:** draft under the same rules with a meaning lock against brief/sources.
- Collapse mechanical detect/replace into a helper CLI so agents do not load the full lexicon or regex-hunt in context.

## Scope / limits

- Skill tree only: `skills/docs/rr-humanize/`. No edits to `docs/`, `refs/commands.md`, `COMPONENT-SPECS.md`, `USAGE.md`, plugin README, or `plugin.json`.
- No detector scores, GPTZero/Turnitin, homoglyphs, disfluency injection, or invented specificity.
- Atlassia `humanizer` stays Jira-only; this pack is general docs/README/MR prose.
- Helper CLI: `scan`, `apply-safe`, `suggest-register` only — not full rewrite, generate, or markdown wipe.

## Audience

- Agents drafting or polishing technical writing (READMEs, MR bodies, internal docs).
- Not for: code comments, API schemas, Jira ticket shape (use Atlassia humanizer), or creative fiction.

## When to use

- User asks to humanize, de-AI, or tighten prose.
- Generate path: load **before** drafting when parent skill or user requests these voice rules.
- Rewrite path: existing text with optional `--voice` / `--tone` flags.
- Words-only or structure-only sub-requests → progressive load via `scan` (see SKILL.md).

## Non-obvious choices

| Choice | Rationale |
|--------|-----------|
| Structure beats vocabulary | Parallel negation, tricolons, copula avoidance are stronger tells than a single banned word |
| `patterns.json` + `lexicon.md` split | Mechanical lists in JSON; judgment (tricolons, when not to replace) in ref only |
| Closed enums `--voice` / `--tone` | Three-by-three set; no lguz named voices or `neutral` duplicate |
| Shell-call budget | Rewrite ≤2 (`scan`, optional `apply-safe`); generate ≤1 `scan` after draft |
| Defaults | Generate → `active` + `plain`; rewrite → `keep` + extract tone (`suggest-register` or `plain`) |

## Load map

| Path | Load when |
|------|-----------|
| `refs/generate.md` | No source text yet; drafting from brief |
| `refs/rewrite.md` | Source text present |
| `refs/readability.md` | Structure pass (always for generate/rewrite LLM step) |
| `refs/lexicon.md` | `scan` hit categories that need judgment |
| `refs/register.md` | Flags unclear or `suggest-register` low confidence |
| `refs/params.md` | User passed CLI-style flags |
| `scripts/README.md` | Invoking helper CLI |

## Shell-call budget

| Action | Max CLI calls |
|--------|----------------|
| Rewrite | 2 (`scan`, optional `apply-safe`) |
| Generate | 1 (`scan` on draft) |

Never a third call in the same action.

## Invoke (helper CLI)

From plugin root (or absolute path):

```bash
python3 skills/docs/rr-humanize/scripts/cli.py scan [path]
python3 skills/docs/rr-humanize/scripts/cli.py apply-safe [--dry-run] [path]
python3 skills/docs/rr-humanize/scripts/cli.py suggest-register [path]
```

Stdin when path omitted. One JSON envelope on stdout — see `scripts/README.md`.

## File structure

```
rr-humanize/
  README.md          # this plan spec
  SKILL.md           # router
  refs/              # generate, rewrite, readability, lexicon, register, params
  scripts/           # cli.py, patterns.json, tests/
```
