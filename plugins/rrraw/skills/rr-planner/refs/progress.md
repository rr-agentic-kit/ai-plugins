# progress

**Owner:** Skill-wide verifying phrases. Mechanical writes stay in `validate_planning.py`.

**Load when:** Every invocation.

## Phrases

Print before the work, then after:

```
verifying <section>
<section> is created
<section> is fixed
<section> was ok
<section> is failed
```

Fail → `<section> is failed`. Stop that section’s work; do not invent another success verb.

Map script TSV `created|fixed|ok|failed` → `is created` / `is fixed` / `was ok` / `is failed`.

## Where

| Path | Sections |
|------|----------|
| `--setup` | [setup.md](setup.md) list; TSV from `validate_planning.py --setup` |
| Resolve rewrite | `cascade format` |
| Resolve `--sync-agent-config` | `agent.plan.md`, `root SoT load line` |
| Freeze mint | `status.yaml` |
| Write `status.yaml` / `agent.plan.md` | those filenames as section names |

Section names are locked in [setup.md](setup.md). Do not paraphrase (`plans dir` ≠ `plans directory`).
