# Generate workflow

Draft new prose from a brief and optional sources. Load after `SKILL.md` router selects generate path.

## Preconditions

- Brief or user intent exists. If empty → ask what to write; stop.
- Read sources before drafting when cited. Lock facts: names, numbers, dates, quotes stay fixed.

## Register defaults

- `--voice active`, `--tone plain` unless user set flags (`refs/params.md`) or brief already addresses the reader (`you` only then).
- High-confidence `suggest-register` on brief prose may override tone; never override voice to `you` without brief signal.

## Meaning lock (both paths)

Never add names, numbers, dates, quotes, or claims not in source or brief.

## Steps

1. **Meaning lock** — List immutable facts from brief/sources (bullet list internal; do not invent).
2. **Draft** — Apply `refs/readability.md` and `refs/register.md` when flags or tone unclear.
3. **Optional scan** — `python3 skills/docs/rr-humanize/scripts/cli.py scan` on draft (≤1 call). Load `refs/lexicon.md` only for judgment categories in `result.hits`.
4. **Reshape** — Fix judgment hits; one substantive pass (reshape, not synonym-swap).
5. **Claim check** — Every sentence traceable to brief/source; no added specificity (places, dates, interviewees).
6. **Deliver** — Output draft only; no detector scores or meta commentary about "humanizing."

## Failures

| Situation | Action |
|-----------|--------|
| Missing source for a required fact | `[VERIFY]` or ask user; do not fabricate |
| Scan empty | Skip lexicon ref |
| Mixed tone in brief | Default `plain` |
