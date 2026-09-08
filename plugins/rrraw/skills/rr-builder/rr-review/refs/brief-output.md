# Review brief — output schema

**Audience:** **rr-review** step 3b.

## Path

`REVIEW_DIR/brief/review-brief-<short-branch>-<RUN_ID>.md`

**Callback:** `Brief written: <path>` — retain **`BRIEF_PATH`**.

## Required body

```markdown
# Review brief
SOURCE STATUS: pr=<resolved|absent|unavailable> issue=<resolved|not linked|unavailable|not relevant> wiki=<resolved|not linked|unavailable|not relevant>
GOAL: <one bounded statement or "unresolved">

## Acceptance and regression signals
## Usage / activation / delivery contract
## Architecture and boundaries
## Related projects, PRs, and contracts
## Open questions
## Out of scope
## Sources
```

## Size cap

**200 lines or 3,500 words**, whichever comes first. Truncation order: GOAL and acceptance first; append `BRIEF TRUNCATED: <N> lower-ranked source detail omitted`.

## Rules

- No CP/AR/test findings — context only.
- Cite URLs or repo paths in **Sources**.
- Conflicting PR vs issue acceptance → note both.
