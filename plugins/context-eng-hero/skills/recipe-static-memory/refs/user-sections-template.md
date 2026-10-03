# User-global section template

Use this **order** for **design** draft and **review** walkthrough when `scope=user` (opt-in only).

Shared SoT path: `~/.agents/AGENTS.md`. Adapters/overlays: `user-global-multi-harness.md`. Same inclusion bar as project: ~90% cross-repo leverage—not a preference dump. Prefer pointers over paste.

| # | Section | Required on design | Home |
|---|---------|-------------------|------|
| 1 | **Communication contract** | Yes — exhaustive | Shared SoT |
| 2 | **Role framing** | Yes — exhaustive | Shared SoT |
| 3 | **Git & commits** | If applicable (and high-leverage) | Shared SoT |
| 4 | **Security** | If applicable | Shared SoT |
| 5 | **Environment** | If applicable | Shared SoT |
| 6 | **Tooling & agents** | Yes on user design if plugins/skills/MCP installed—trigger table per `tooling-orchestration.md`; waive only explicit | Shared SoT (§6 = cross-harness triggers); harness-native rows → overlay |
| 7 | **Non-goals** | Recommended | Shared SoT |
| 8 | **Harness overlays** | Per selected harness if harness-only constraints exist | `~/.agents/{HARNESS}.specific.md` |
| 9 | **Imports** | If `@` always-on splits used (never `@` situational packs) | Claude adapter / approved SoT splits only |
| 10 | **Situational packs** | Only if packs exist — backtick + when-to-Read | Rare for user-global; same rules as project |

## Section header style

Use `##` headings matching names above for SoT sections. Under each: bullet list only unless user requests prose. Overlay files use short harness-specific headings (models, Task/subagent, harness quirks)—not a second copy of comm/role.

## Missing sections

On **review**: show `(missing)` and default **Deep-dive** for rows 1–2; for 3–7 offer Accept only if user explicitly waives bucket; **delete** low-leverage bullets. For row 8: if adapter exists but overlay missing and harness-only content sits in SoT or adapter body → challenge → split (user confirm).
