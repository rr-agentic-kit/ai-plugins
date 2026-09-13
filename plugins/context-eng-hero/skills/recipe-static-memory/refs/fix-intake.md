# Fix intake — symptom → layer

**Fix** is minimal and symptom-led. **Not** a full redesign.

## Stop → route to design

- User wants a **totally different persona** or outcome
- Always-on file empty or missing
- More than half the file wrong structurally

## Symptom map

| Symptom | Likely layer |
|---------|--------------|
| Too verbose / wall of text | User-global Communication contract |
| Never pushes back | Communication + Role |
| Wrong expertise level | Role framing |
| Commits without asking | Git & commits |
| Ignores test / build command | Always-on **Commands** (or missing situational trigger) |
| Uses wrong package manager | Always-on **Stack** / **Commands** |
| Leaks other repo conventions | User-global project leak; move to project `AGENTS.md` |
| Sycophantic openers | Communication contract |
| Over-explains basics | Role — seniority assumption |
| Ignored installed skill / wrong tool / improvised instead of MCP | Tooling & agents (§6) |
| Never uses explore subagent on large repos | Tooling & agents (§6) |
| Burns tokens with huge always-on / `@` pack imports | Always-on bloat or forbidden `@.agents/` — cut or move to backtick trigger |
| Misses depth only needed in a recurring niche | Missing situational Read trigger / pack (only if `situation-groups.md` justifies) |
| Agent invents process already in CONTRIBUTING | Belongs in **docs** — add pointer, do not paste |

## Scope guard

- One symptom cluster per fix pass unless user lists multiple
- No new sections/packs unless required to fix the symptom **and** inclusion bar passes
- Prefer “see `CONTRIBUTING.md` / README” over absorbing docs
- Comm/role touch → load `communication-role-exhaustive.md` for **failing dimensions only**
- §6 / tooling touch → load `tooling-orchestration.md` for **gap triggers/modes only**

## Evidence

Prefer quoted offending bullets or a short session example from the user.
