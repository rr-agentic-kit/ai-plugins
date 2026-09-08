# Review artifacts (.rr-builder)

**Purpose:** Canonical paths for **rr-review** runs. Paths are at the **repository root** of the project under review.

**Disk write contract:** Mint **`runId`** once. Every lane uses the same **`REVIEW_DIR`**. `mkdir -p` via Shell; persist markdown with Write.

## Run id

**Format:** `MM-DD-HH-mm-ss` local wall clock. Collision: append `-2`, `-3`, …

## Layout

**Root:** `.rr-builder/{runId}/`

```
.rr-builder/{runId}/
  report.md
  scope-preflight.json   # ci only
  brief/
  code/
  test/assess/
  security/
  plans/                 # fix SoT
```

| Lane | Path | Pattern |
|------|------|---------|
| Merged report | `report.md` | single file |
| CI preflight | `scope-preflight.json` | rr-ci envelope |
| Brief | `brief/` | `review-brief-<short-branch>-<runId>.md` |
| Code assess | `code/` | `code-review-<short-branch>-<runId>[-<chunk>].md` |
| Test assess | `test/assess/` | `tra-<short-branch>-<runId>[-<chunk>].md` |
| Security | `security/` | `security-audit-<short-branch>-<runId>[-<chunk>].md` |
| Fix plans | `plans/` | `trp-<short-branch>-<runId>.md` |

Multi-chunk: suffix assess stems with slug of `chunk_id` (slashes → `--`).

## `.gitignore` (consumer repos)

Recommended: ignore `.rr-builder/` or entire `.ai/` for local-only AI output.

## Related

- Params: [params.md](params.md)
- Brief: [brief-output.md](brief-output.md)
