# Effective static memory writing

## Testable bullets

**Bad:** Be concise.  
**Good:** Lead with recommendation in ≤2 sentences before detail. Max 3 paragraphs unless user asks for depth.

**Bad:** Act as senior engineer.  
**Good:** Act as principal architect: state tradeoffs A vs B with cost; challenge wrong problem framing before implementing.

## Line budgets

| File | Target |
|------|--------|
| User-global | ~100 lines (comm/role may use `@import` or ~60–80 inline) |
| Project | ≤200 lines |

## Stale content

- Dates or version numbers without “verify in repo” → flag on review
- References to removed tools → fix or delete
- Project names from old jobs in user-global → move or delete

## Micro-examples in bullets

One short example per non-obvious rule is enough—no essay paragraphs inside bullets.
