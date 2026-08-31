# Register (voice and tone)

Map `--voice` and `--tone` flags (or `suggest-register` output) to concrete style constraints. Unknown values → `refs/params.md` error line.

## Voice (`--voice`)

| Value | Use |
|-------|-----|
| `active` | Default for generate. Active SVO; avoid puffery copulas. |
| `you` | How-tos and instructions when brief or user requests reader address. |
| `keep` | Default for rewrite. Match source person (I/we/you/impersonal). |

There is no useful `--voice passive` goal.

## Tone (`--tone`)

| Value | Use |
|-------|-----|
| `plain` | Docs, READMEs, reference. Neutral, no personality theater. Default when mixed signals. |
| `firm` | Decisions, MR bodies. Fewer empty hedges; direct obligations. |
| `warm` | Professional-warm. Contractions OK; no slang or anecdotes. |

Dropped: `neutral` (same as plain), `casual`/`storyteller`, `direct` (fold into `you`).

## Defaults

| Path | Voice | Tone |
|------|-------|------|
| Generate | `active` | `plain` |
| Rewrite | `keep` | from `suggest-register` or `plain` |

## suggest-register

CLI heuristic: pronoun rates, hedge density, contraction rate → `{ voice, tone, confidence }`.

- `confidence` ≥ 0.7 → use result; skip this ref.
- `confidence` < 0.7 → apply table above with user flags winning.

## Tone application

| Tone | Contractions | Hedges |
|------|--------------|--------|
| plain | optional | keep factual only |
| firm | optional | remove empty; keep factual |
| warm | prefer | keep factual; avoid stiff formality |

## Address

- `--voice you` only when user set it or source/brief already uses second person.
- Do not flip impersonal report prose to `you` on rewrite unless flagged.
