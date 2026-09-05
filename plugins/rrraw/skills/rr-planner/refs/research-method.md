# research-method

**Owner:** Post-composition market evaluation methodology — broad competitor/market/standards research with citations.

**Load when:** `--research` action or `depth: deep` chain appends research phase.

## When research runs

Research is a **distinct, later phase** — after docs are composed:

1. Evaluates the market against finished planning docs.
2. Broader and deeper than discovery-time targeted searches ([proactivity.md](proactivity.md)).
3. Feeds refinement signals back to skill/user for optional re-discover.

## Research scope

| Area | Evaluate against |
|------|------------------|
| Competitive landscape | MRD competitors section, PRD differentiation |
| Market sizing / trends | MRD segments, executive-summary "why now" |
| Standards / regulations | BRD business rules, PRD NFRs (mechanism → spine / feature delta) |
| Technology landscape | Standing architecture + deltas; Discover may park early notes in `tech.md` |
| Customer evidence | PRD personas **section**, MRD customer needs |

## Iterative research

**Agent (one Task invocation):** iterations until no new material findings in an iteration. Each iteration: plan queries → search → synthesize → check gaps. Per iteration: 3–5 queries (not unlimited). No fixed round cap. Then return `ok` or `partial` — do not wait for user confirm.

**Skill:** after the agent returns, user confirms done (may re-`Task`) or stop / pause (checkpoint and exit).

Per iteration:

1. Read all composed docs in `--output-dir`.
2. Extract claims marked `validated: false` or lacking citations.
3. Prioritize: blocking assumptions > competitive gaps > nice-to-have.
4. Plan 3–5 queries per iteration (not unlimited).
5. Execute searches; record citations.

## Citation format

```json
{
  "title": "Source title",
  "url": "https://...",
  "accessed": "2026-06-24",
  "relevance": "One sentence on why this source matters",
  "quote_or_paraphrase": "Key fact extracted"
}
```

Rules:

- No unsourced factual claims in findings.
- Prefer primary sources (vendor docs, regulatory sites, SEC filings) over aggregators.
- Mark conflicting sources explicitly.

## Finding synthesis

Per finding:

| Field | Content |
|-------|---------|
| `impact` | `confirms` — supports doc claim; `contradicts` — conflicts; `extends` — adds new info |
| `affected_docs` | Which docs need refinement |
| `refinement_signals` | Specific section + suggested change |

## Clarifications

Research agent returns `clarifications_needed[]` when:

- Docs contain contradictory claims research cannot reconcile.
- Critical assumption is untestable without user input.
- Scope of research is ambiguous (which market? which timeframe?).

Skill surfaces per `question_mode`; re-invokes research with answers.

## Output integration

Research does **not** auto-edit docs. Skill presents:

1. Findings summary with citations.
2. Refinement signals per doc.
3. User chooses: accept as-is, re-run `--discover` for affected levels, or manual edit.
