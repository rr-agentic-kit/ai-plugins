# Rewrite workflow

Reshape existing prose. Preserve claims; change structure and wording.

## Preconditions

- Non-empty source text. If empty → ask for text; stop.
- Parse flags if present → `refs/params.md`.

## Meaning lock

Preserve all factual claims from source; never add names, numbers, dates, quotes, or new assertions.

## Steps

1. **Scan** — `python3 skills/docs/humanize/scripts/cli.py scan [path]` (required; counts toward budget).
2. **Meaning lock** — Extract claims, entities, numbers, hedges that express real uncertainty. Do not delete factual uncertainty when `--tone firm` (see `refs/lexicon.md`).
3. **Apply-safe** (optional, second call max) — `apply-safe [--dry-run]` for `result.auto_fixable` only. Do not use if scan reports no auto-fixable hits.
4. **LLM reshape** — Load `refs/readability.md`. Load `refs/lexicon.md` only for categories in `result.hits` with `needs_judgment: true` per hit or category.
5. **Register** — Default `--voice keep`. Run `suggest-register` on source; if confidence ≥ 0.7 use result, else `refs/register.md`. User flags win.
6. **Claim check** — Output must not add/remove factual claims vs source.
7. **Deliver** — Rewritten text only.

## Shell-call budget

≤2 calls: `scan` + optional `apply-safe`. Reshape is LLM, not a third CLI call.

## Judgment vs mechanical

| Scan signal | Handler |
|-------------|---------|
| `auto_fixable` | `apply-safe` or manual same replacement |
| `needs_judgment` | LLM + `refs/lexicon.md` |
| `stats` only | Hints; not pass/fail |
