# User-global section template

Use this **order** for **design** draft and **review** walkthrough when `scope=user` (opt-in only).

Same inclusion bar as project: ~90% cross-repo leverage—not a preference dump. Prefer pointers over paste.

| # | Section | Required on design |
|---|---------|-------------------|
| 1 | **Communication contract** | Yes — exhaustive |
| 2 | **Role framing** | Yes — exhaustive |
| 3 | **Git & commits** | If applicable (and high-leverage) |
| 4 | **Security** | If applicable |
| 5 | **Environment** | If applicable |
| 6 | **Tooling & agents** | Yes on user design if plugins/skills/MCP installed—trigger table per `tooling-orchestration.md`; waive only explicit |
| 7 | **Non-goals** | Recommended |
| 8 | **Imports** | If `@` always-on splits used (never `@` situational packs) |
| 9 | **Situational packs** | Only if packs exist — backtick + when-to-Read |

## Section header style

Use `##` headings matching names above. Under each: bullet list only unless user requests prose.

## Missing sections

On **review**: show `(missing)` and default **Deep-dive** for rows 1–2; for 3–7 offer Accept only if user explicitly waives bucket; **delete** low-leverage bullets.
