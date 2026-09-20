# Situation groups — derive, don’t catalog

Situational packs live at `.agents/{group}.md`. **No fixed catalog.** Do not ship or assume `testing.md` / `safety.md` / `contributing.md` as defaults.

## When a pack is justified

Create `.agents/{group}.md` **only if** leftover content:

1. Fails the always-on budget after applying the 90% bar, **and**
2. Still passes ~90% usefulness **when that situation hits**, **and**
3. Is **not** better left as a pointer to README / CONTRIBUTING / ADRs / plugin docs

Zero packs is preferred. Few stable groups beat many thin files.

## How to invent group names

Derive from **this** project’s evidence:

1. What would bloat `AGENTS.md` past budget after the 90% bar
2. Natural clusters in *this* repo’s agent-relevant constraints
3. Stable names that won’t churn (prefer merge over rename)

Examples (illustrative only—not a checklist): `monorepo-install.md`, `release-train.md`, `legacy-cobol.md`—whatever clusters *here*.

## Always-on vs situational vs docs

| Layer | Heuristic |
|-------|-----------|
| Always-on (`AGENTS.md`) | Wrong-every-time when missing |
| Situational (`.agents/{group}.md`) | Often-needed depth idle in most chats |
| Docs (README, CONTRIBUTING, …) | Human/project truth outside agent memory |

## When **not** to create a pack

- Topic lives better as “see `CONTRIBUTING.md`” → pointer in `AGENTS.md` only
- Content fails the 90% bar even in its niche → omit or put in a skill/command
- Would duplicate an existing authoritative doc → pointer, never mirror
- Only created to “have a testing/safety section” → anti-pattern

## Collision with `.agents/skills/`

Cursor Agent Skills use `.agents/skills/`. Instruction packs are **flat** `.agents/{group}.md` only. Never write packs under `.agents/skills/`.

**Reserved:** `.agents/local.md` is the gitignored personal override—not a derived situational group name. Do not invent a shared pack named `local`.

## Indexing in always-on

When packs exist, add a short situational index in `AGENTS.md`:

```markdown
## Situational packs

| When | Read |
|------|------|
| Writing / changing tests in this monorepo | `.agents/{derived-name}.md` |
```

Omit the index section entirely when there are zero packs.

## Anti-rewrite

Rename or split groups only on explicit redesign. Prefer merging related depth into one stable file.
