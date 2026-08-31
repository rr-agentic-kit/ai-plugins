# Lexicon (judgment)

Apply replacement judgment for `scan` hits the CLI cannot auto-fix. Mechanical lists live in `scripts/patterns.json` only.

## Load when

`scan` reports hits in: `banned_word`, `copula_avoidance` (non-auto), `transition_cluster`, `not_x_but_y`, or `em_dash`.

Skip when scan is empty or only auto-fixable `filler` / `chatbot`.

## banned_word hits

- Inflated verbs/nouns (`leverage`, `utilize`, `facilitate`, `streamline`, `robust`, `comprehensive`, `delve`, `pivotal`, `realm`, `meticulous`, `underscore`): plain verb, specific fact, or drop if vague.
- Formal openers (`Indeed`, `Furthermore`, `However`, `Notably`, `Additionally`, `Moreover`, `Therefore`, etc.): ≤1 per paragraph; prefer `so`, `but`, `also`, `then`.

## Copula avoidance (judgment)

- `serves as` → `is` when auto-fixable; `functions as`, `acts as` → check whether `is` loses nuance.
- `boasts`, `features` → `has` only when listing facts, not marketing tone.

## not-X-but-Y

Heuristic flag only. Rewrite when the contrast is rhetorical, not factual:

- Rhetorical: "It's not just a tool, it's a platform" → state what it is.
- Factual contrast: keep when negation carries real information from source.

## Hedges

| Delete (empty) | Keep (factual) |
|----------------|----------------|
| "it is important to note", "kindly", "at this point in time" | "may", "might" when source uncertainty is real |
| "as discussed" without referent | Documented risk or unknown scope from source |

`--tone firm`: trim empty hedges; keep uncertainty that matches source.

## Transition clusters

≥2 sentences in a row starting with formal pivots (see ban list) → merge or relead one sentence.

## Em dashes

Prefer two sentences or comma when the dash only adds drama. Keep when separating a legitimate appositive from source.

## Invariants

- Do not add ban-list words while fixing.
- Do not invent names, numbers, or quotes.
- One substantive reshape pass minimum — synonym swap alone fails.
