# progress

**Owner:** Skill-wide verifying phrases + close / Next Up habits that enforce [INTENT.md](../../INTENT.md) UX (user is not process-owner).

**Load when:** Every invocation.

**Layer SoT:** [challenge-layers.md](challenge-layers.md). Version mint: [baselines.md](baselines.md).

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
| `--setup` | [setup.md](setup.md) list; TSV from `validate_planning.sh --setup` |
| Resolve rewrite | `cascade format` |
| Resolve `--sync-agent-config` | `agent.plan.md`, `root SoT load line` |
| Freeze mint | `status.yaml` |
| Write `status.yaml` / `agent.plan.md` | those filenames as section names |
| Intake situate / absorb / challenge / select / mint / detail / ready | `intake situate`, `intake docs`, `intake challenge`, `intake select`, `intake mint`, `intake detail`, `intake ready` |

Section names are locked in [setup.md](setup.md). Do not paraphrase (`plans dir` ≠ `plans directory`).

## Next Up / close (process-ownership)

Skill owns the close offer. User supplies product judgment and **risk acceptance**, not ceremony memory.

| Rule | |
|------|--|
| No skip-incentivize | Do not frame “move on” / “skip challenge” as the happy path to freeze |
| Freeze auto-suggest | Only after **standard** challenge clear (or risk-accept) for the freeze unit — [challenge-layers.md](challenge-layers.md) |
| Smell-clean alone | Never the freeze Next-Up |
| Open queues | When `checkpoint.pending_clarifications` is non-empty **or** open challenge findings await absorb → Next Up = drain Qs / remediations (cheaper-first ladder), **not** challenge / re-attest — [challenge-layers.md](challenge-layers.md) |
| Close-challenges NL | NL “close open challenges” / “ask until challenges close” → Next Up = drain dirty `challenge.*` stems + pending (cheaper-first). **Anti-trigger:** forbid inventing standing/spine/dual-lens redesign sitting under that ask — Plan [input-resolution.md](../../skills/rr-planner/refs/input-resolution.md) NL |
| QPC ≠ challenge | Answering a `questions_per_cycle` batch never makes challenge the Next Up by itself |
| Advance without finishing | Allowed when solid subset is load-bearing-stable; skill drives downstream impact on upstream change |
| Risk-accept | Concrete AskQuestion → stamp `dirty-accepted` on named stems; record reasoning |
| Quality veto | Refuse freeze-by-say-so over open quality debt without risk-accept |

Discover Next Up after BRD freeze → Plan. Plan Next Up after slice freeze → future Execute. Mid-chain: goal-likelihood / challenge / reopen work — not freeze-by-default. When open queues block challenge, offer drain first; challenge only after the pre-Task probe passes.

## Intake pipeline Next Up

Shared stages: [intake.md](intake.md). AskQuestion options = **legal pipeline moves only** (never “skip to code”).

| Stage / block | Phrase / section | Next Up |
|---------------|------------------|---------|
| Situate | `intake situate` | Report match class + first blocking stage |
| Docs gap (2) | `intake docs` | Planner absorb / `--intake` |
| Cohesion / Discover-arch drift (3) | `intake challenge` | Plan challenge / Discover reopen / baselines Ask / risk-accept — **block code** |
| Select / slice (4) | `intake select` | Thin select or planner select |
| No task (5) | `intake mint` | Builder mint after 2–4 PASS |
| Thin task (6) | `intake detail` | Goal/Steps / plan stage |
| Ready (1–6 PASS) | `intake ready` | **`--feature`** (default) or **`--adhoc`** (urgent) or orchestrate `--task`/`--step` |
| Planner intake done | — | Peer **rr-builder** `--feature` / `--adhoc` for stages 5–7 — planner never codes |
| Builder stage-3 block | — | Peer-invoke planner/discovery SKILL; resume intake/`--feature`/`--adhoc` only after return |

**Anti-triggers on close:** do not offer “code now” while stages 2–6 incomplete on rr; do not frame obligation-only task body as substitute for docs absorb.
