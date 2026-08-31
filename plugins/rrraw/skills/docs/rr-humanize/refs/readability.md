# Readability

Apply structure and flow rules in the LLM reshape step (not scripted).

## Structure tells (fix first)

| Pattern | Detect | Fix |
|---------|--------|-----|
| Parallel negation | "Not only… but also…", "It's not X, it's Y" stacked | State the positive claim once |
| Tricolon / rule of three | Three parallel phrases where one suffices | Cut to one or two; keep if list is factual |
| Rhetorical Q+A | Question immediately answered in next sentence | Merge or drop the question |
| Mirror sentences | Same opener or shape 3+ times in a row | Vary length and lead |
| Significance inflation | "pivotal", "landscape", "testament", "underscores the importance" | Plain verb or drop |
| Copula avoidance | "serves as", "stands as", "boasts", "features" for simple `is`/`has` | Prefer `is`/`has` when meaning unchanged |

## Psych / flow

- **Given–new:** start sentence with known info; end with the new point.
- **One idea per sentence** — split stacked clauses.
- **SVO close:** subject–verb–object near the start when possible.
- **Chunking:** short lead sentence, then detail.
- **Repeat key nouns** — avoid elegant variation that hides the referent.

## Punctuation

- Prefer period or comma over em dash, semicolon glue, or mid-clause colon.
- `scan` reports `em_dash` count as a hint; judgment on whether to split.

## Sentence rhythm

- Mix short and long sentences; avoid uniform ~18-word runs.
- No quota for unresolved endings or mandatory "And/But" — soft guidance only.

## Do not script here

Tricolon removal, paragraph reorder, and given–new restructure require LLM judgment. `scan` surfaces hints; this ref guides the pass.
