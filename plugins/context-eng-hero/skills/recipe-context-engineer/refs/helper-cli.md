# Helper CLI (scripts executed, not loaded)

When a skill folder includes `scripts/`, the agent **runs** them via shell—it does **not** load script source into context as documentation.

Load with **create**, **fix**, **design**, and **audit** when `scripts/` exists under the target skill.

## Core rule

| Do | Do not |
|----|--------|
| Document **invoke line**, args, stdout shape, exit codes in SKILL or a short `scripts/README.md` | Paste full Python/bash into SKILL body |
| Point Procedure to `python3 scripts/<tool>.py …` or `allowed-tools: Bash(…)` | Treat scripts as progressive-disclosure refs to Read |
| One envelope on stdout when output is machine-parsed | Multi-step shell chains the agent reinvents every turn |

Anthropic agent-skills guidance: scripts are **executed**, not loaded as docs.

## When to add `scripts/`

- Repeatable multi-step workflow where the agent would otherwise invent the same shell chain every time
- Deterministic structure checks (see plugin `scripts/audit_static.py` as reference)
- Fat CLI that polls internally so the agent waits one invocation

**Not for:** one-off `git`/`glab` calls documented once; general SDK layers; inline bash chains that belong in a single documented command.

## Design goals

1. **One agent shell call per workflow step** — collapse chains into one entry point.
2. **Stable stdout** — JSON envelope or fixed columns when the agent branches on output; stderr for human progress only.
3. **Domain logic in Python** — state machines, poll loops, preflight; thin transport.
4. **Fixture-driven tests** — when tests exist in monorepo; installed plugin may ship without pytest (see plugin root `CLAUDE.md`).

## SKILL authoring pattern

```markdown
## Procedure

1. From plugin root, run `python3 scripts/my_tool.py <args>` (see `scripts/README.md`).
2. Parse stdout; on non-zero exit, stop and report stderr tail.
```

Optional frontmatter:

```yaml
allowed-tools: Bash(python3 scripts/my_tool.py*)
```

## Skill + Ref progressive disclosure

- **SKILL.md** — invariant procedure + when to run which script.
- **`refs/<variant>.md`** — variant flags or output interpretation—linked **one hop** from SKILL **Progressive disclosure**; ref does not link to further refs.
- **`scripts/`** — implementation; README lists subcommands only.

## Forcing test

“Does this reduce agent shell calls, tokens, or duplicated script lines—or only change internal transport?” If only internal transport, keep the existing approach.
