# humanize CLI

Stdlib-only helper for mechanical detect/replace. **Stdout:** one JSON object per run. Parse JSON only.

## Invoke

From plugin root (or absolute path):

```bash
python3 skills/docs/rr-humanize/scripts/cli.py scan [path]
python3 skills/docs/rr-humanize/scripts/cli.py apply-safe [--dry-run] [path]
python3 skills/docs/rr-humanize/scripts/cli.py suggest-register [path]
```

Omit `path` to read stdin. Exit `0` on success; `1` on failure; `2` on usage (argparse).

## Envelope

```json
{
  "command": "scan",
  "ok": true,
  "result": { "hits": {}, "auto_fixable": false, "needs_judgment": true, "stats": {} },
  "error": null
}
```

On failure: `"ok": false`, `"error": { "code": "...", "message": "..." }`.

## Commands

| Command | `result` keys agents branch on |
|---------|----------------------------------|
| `scan` | `hits`, `auto_fixable`, `needs_judgment`, `stats` |
| `apply-safe` | `changed`, `changes`, `text` or `preview` (dry-run) |
| `suggest-register` | `voice`, `tone`, `confidence`, `signals` |

Mechanical patterns: `patterns.json` (source of truth). Judgment rules: `refs/lexicon.md` only.

## Design

Helper CLI rules: [`../../../context/context-engineer/refs/helper-cli.md`](../../../context/context-engineer/refs/helper-cli.md). Shell-call budget: [`../README.md`](../README.md).

## Tests

```bash
python3 -m unittest discover -s skills/docs/rr-humanize/scripts/tests -p 'test_*.py'
```

From plugin root. Fixtures live under `scripts/tests/fixtures/`.
