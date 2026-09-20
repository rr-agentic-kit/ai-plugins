# Effective static memory writing

## Inclusion bar (90% filter)

Before every bullet: does this improve or prevent mistakes in **~90%+** of chats?

| Keep | Cut / redirect |
|------|----------------|
| Hard rules agents violate without them | Rare workflows → skill, command, or omit |
| Stack + essential copy-paste commands | Full quality matrices → `CONTRIBUTING.md` pointer |
| Short where-to-look for agent-critical paths | Narrative product docs → README |
| Non-goals that stop recurring wrong work | “Nice to have” preferences that almost never fire |

Challenge user requests that fail the bar. Prefer **pointer over paste**.

## Testable bullets

**Bad:** Be concise.  
**Good:** Lead with recommendation in ≤2 sentences before detail. Max 3 paragraphs unless user asks for depth.

**Bad:** Act as senior engineer.  
**Good:** Act as principal architect: state tradeoffs A vs B with cost; challenge wrong problem framing before implementing.

## Line budgets

| File | Target |
|------|--------|
| `AGENTS.md` (always-on) | Tight: prefer lean over exhaustive; cut before inventing packs |
| User-global always-on | ~100 lines (comm/role may use `@import` of always-on splits or ~60–80 inline) |
| `.agents/{group}.md` | Only if leftover fails always-on budget **and** still passes ~90% when that situation hits |
| `CLAUDE.md` | Thin pointer (`@AGENTS.md`) + rare Claude-only bullets |

Zero packs is valid. Do not fill sections to match a template—omit empty leverage.

## Load-rule writing

- `CLAUDE.md`: `@AGENTS.md` for always-on; optional `@.agents/local.md` (gitignored personal).
- Situational: backticked path + **when-to-Read** trigger in `AGENTS.md`.
- **Forbid** `@` of shared situational packs; only `.agents/local.md` may be `@`-imported.

## Pointer over paste

```markdown
# Good
Full quality matrix: see `CONTRIBUTING.md`.

# Bad
(paste entire CONTRIBUTING quality section into AGENTS.md)
```

## Stale content

- Dates or version numbers without “verify in repo” → flag on review
- References to removed tools → fix or delete
- Project names from old jobs in user-global → move or delete
- Low-leverage bullets → **delete** on review (do not keep for completeness)

## Micro-examples in bullets

One short example per non-obvious rule is enough—no essay paragraphs inside bullets.

## Anti-rewrite

Fewer stable situational groups; rename packs only on explicit redesign. Prefer merge over many thin files.
