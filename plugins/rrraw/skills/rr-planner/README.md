# rr-planner

Flag-driven **Plan**: honest Effort + buildable slice handoff from a frozen `business-case.yaml`. Human index only — runtime is [SKILL.md](SKILL.md) + [refs/](refs/).

## Why

Specify what to build after Discover proved the bet — with system judgment in the same sitting so RICE Effort is trustworthy and Execute does not invent mechanism or cost-driving UX shape. Refuse Effort-without-architecture, Effort without cost-driver cites, requirement-table shrink-to-ship, smell-fail AC, sprint ceremony, silent PRD inventiveness when BRD is not frozen, and **silent full-load of fat plan docs**. **Success** = raises the odds the builder reaches the frozen Discover objective / OMTM — Effort honesty + pin-complete kernel are necessary preconditions, not the finish line. Freeze only when further Plan work stops moving that likelihood and no open standing red flag / Discover-reopen blocks it — **not** product-doc section coverage or smell-clean ceremony.

## What

Owns Plan Q&A, PRD compose/change, standing **constitution** (always-load INDEX; Plan-owned tech + global UX baseline), on-demand **tech ADRs** (`architecture.md`), feature deltas (decision-lite mechanism, Effort drivers, UX-shape), WWAS AC, selection status, slice freeze (`execute-slice.yaml`), research, technical challenge (pre-mortem + red-team), and **context-budget detect / `--optimize`**. Discover (ES→MRD→BRD + business-case) is `rr-discovery`. Cascade `.md` persists only after `skills/rr-discovery/refs/compose-prose.md` → `rr-humanize`.

**Context budget:** `scripts/context_budget.sh` (tiktoken soft≥5k / hard≥8k). Dual-runtime plugin hooks (Cursor `hooks/cursor.json` + Claude `hooks/hooks.json`) inject soft/hard attention receipts when plan docs grow or the prompt mentions `rr-planner`. Skill detect after `standing` and before research/challenge; hard → `CONTEXT_BUDGET_EXCEEDED` + scoped load — not auto-rewrite. SoT: [refs/context-budget.md](refs/context-budget.md). Monorepo hook authoring: `.agents/hooks.md`.

**Explicitly no traditional sprints** (no capacity/velocity theater). Sequencing language: **slice / phase / selected requirements**. Release/version bundling of frozen slices is a later Plan add-on — not this skill’s inventiveness.

**Out of scope:** Execute / ship-check / ticket writing — future. Execute starts fused code+test from the kernel; no separate tech-planning step in Plan.

## Actions

| id | outcome | pick when |
|----|---------|-----------|
| `setup` | docs/ framework bootstrap | Shared setup |
| `prd` | Compose PRD + standing Plan path | Entry gate passed |
| `change` | Patch PRD / delta / AC section | `--change` + section + target |
| `freeze-slice` | Mint `execute-slice.yaml` + stamp slice | Selected requirements + standard challenge clear or risk-accept (smell-clean alone insufficient) + Effort drivers |
| `research` | Cited findings on existing docs (scoped load) | Post-compose |
| `challenge` | Technical pre-mortem + red-team (**standard**; add `deep` for exhaustive) | Prefer Plan targets; compact parent summary |
| `optimize` | Suggest rewrite/split/refile alternatives for soft/hard docs | `--optimize` / NL context budget |

`--resume` is a **selector** (continue Plan checkpoint), not a primary action — [input-resolution.md](refs/input-resolution.md).

## When

### Use when

- Frozen BRD + `business-case.yaml` exist and you need Plan (`--prd`, `--change`, `--freeze-slice`)
- Research or challenge **Plan** docs (`--research`, `--challenge`) with scoped load
- Plan docs hit soft/hard token tiers (`--optimize`) or ambient hook attention
- Shared `--setup` or continue a paused Plan session (`--resume` selector)

### Avoid when

- Problem, market, viability, ideation, beachhead → `rr-discovery`
- Starting Plan without freeze + handoff (entry gate)
- Asking for sprint planning / velocity as Plan process
- Asking this skill to invent a release/version plan this pass
- Expecting silent auto-rewrite of fat docs without AskQuestion

## Philosophy

- **Goal-likelihood over ceremony** — Plan succeeds when it raises builder→Discover-objective odds; freeze is a gate when marginal Plan work stops moving that likelihood — not the north-star
- **Layered scrutiny** — Auto-reflection → smells → `--challenge` (standard) → `--challenge deep` (`refs/planning/challenge-layers.md`); smell-clean ≠ challenged
- **Honest Effort** — Dual-lens sitting; `_effort_:` only with same-sitting Decision + Effort drivers (UX cost drivers when UI-facing)
- **Buildable handoff** — Constraints cite deltas; pins + `delta_paths` exist; draft ≠ missing standing law; constitution + deltas beat fat PRD dumps
- **Context budget** — tiktoken detect; constitution-primary always-load; architecture = tech ADRs only; `--optimize` suggest→AskQuestion→apply
- **Full scope honesty + thin selection** — `_status_:` never deletes the requirement table; entry gate = frozen BRD + valid `business-case.yaml`
- **Nature reflection** — Reflect on product nature → derive expectations for this project → elicit; do not wait for a founder dump or dump a universal checklist

## UX

Process-ownership (user is not process-owner): `INTENT.md` UX. Skill-local chrome below.

### Invoke

Flags (`--setup` / `--prd` / `--change` / `--freeze-slice` / `--research` / `--challenge` / `--challenge deep` / `--optimize` / …) or clear Plan NL; bare invoke never silent-composes without entry gate.

### Intake

Status-first (`rrr-status` → phase `status.yaml` + session-state **via** `scripts/session_state.sh view`); resolve emits payload before Plan body. Entry gate also reads discovery freeze + handoff. Solid-subset Plan body on draft Discover allowed when cited subset is load-bearing-stable — freeze mint still needs frozen parents ([input-resolution.md](refs/input-resolution.md)).

### Clarify

AskQuestion on entry-gate fail, vague posture/`domain_context`, binding panel `hold`, smell-fail AC, missing freeze fields, optimize alternative pick, or **risk-accept** — do not invent. Cap stays `questions_per_cycle`.

### Output

PRD + standing constitution/deltas (+ tech ADRs on demand) + WWAS AC + selection status; slice freeze kernel when requested; research/challenge reports (standard/deep only); optimize apply after confirm; cascade prose only after humanize.

### Close

Session-state + status stamps written. **Next Up** per `refs/planning/progress.md`: offer slice freeze only after standard challenge clear (or risk-accept) + auto-reflection / red-flag / Discover-reopen check ([cascade.md](refs/cascade.md), [execute-handoff.md](refs/execute-handoff.md)); after hard budget → `--optimize`; after freeze → Execute (future); after compose → research/challenge or goal-likelihood gap work — **not** freeze-by-default after smell-clean. Do not incentivize skip.

## Technique index

| Technique | Ref |
|-----------|-----|
| Cascade / Plan gates | [refs/cascade.md](refs/cascade.md) |
| Context budget / optimize | [refs/context-budget.md](refs/context-budget.md) |
| Project posture | [refs/project-posture.md](refs/project-posture.md) |
| Goal anchor / clarify | [refs/goal-anchor.md](refs/goal-anchor.md) |
| Note sessions | [refs/note-sessions.md](refs/note-sessions.md) |
| Expert panel / Gate 7 | [refs/expert-panel.md](refs/expert-panel.md) |
| Domain routing | [refs/domain-routing.md](refs/domain-routing.md) |
| Blind spots | [refs/blind-spots.md](refs/blind-spots.md) |
| Coach / Fast interview | [refs/plan-interview.md](refs/plan-interview.md) |
| Nature expectation method | [refs/nature-expectation-packs.md](refs/nature-expectation-packs.md) |
| RICE / RIC / on-demand lenses | [refs/prioritization-lens.md](refs/prioritization-lens.md) |
| Same-sitting system design | [refs/system-design.md](refs/system-design.md) |
| Decision-lite / supersede | [refs/decision-lite.md](refs/decision-lite.md) |
| Constitution (standing law) | [refs/doc-standards/constitution.md](refs/doc-standards/constitution.md) |
| Architecture (tech ADRs) | [refs/doc-standards/architecture.md](refs/doc-standards/architecture.md) |
| Feature deltas | [refs/doc-standards/feature-delta.md](refs/doc-standards/feature-delta.md) |
| WWAS + smell gate | [refs/req-smell.md](refs/req-smell.md) |
| Slice freeze kernel | [refs/execute-handoff.md](refs/execute-handoff.md) |
| Technical challenge | [refs/challenge-method.md](refs/challenge-method.md) |
| Research method | [refs/research-method.md](refs/research-method.md) |
| Pre-save proactivity | [refs/proactivity.md](refs/proactivity.md) |

## Constraints

- **Invoke:** Auto — no `disable-model-invocation`; ambient WHEN description is enough
- **Gates:** Entry gate (frozen BRD + handoff); humanize before cascade `.md` persist; Effort requires standing record + Effort drivers this pass; smell-fail / hollow kernel blocks freeze; hard context budget blocks full-load (`CONTEXT_BUDGET_EXCEEDED`)
- **Paths:** Plugin-root relative only — no `..` in skill/ref markdown
- **Dual-runtime:** Hooks + scripts ship for Cursor and Claude; document any parity gap
- **Eval-first:** Fix FAIL audit ids only; preserve Plan outcome (no redesign)

## Design notes

- **Goal-likelihood vs ceremony** — Freeze when marginal Plan work stops moving builder→OMTM odds; smell-clean / section coverage alone never unlocks freeze-suggest
- **Constitution-primary vs fat PRD** — Always-load INDEX + on-demand deltas/ADRs; refuse corpus dump under hard context budget
- **Suggest-not-auto-rewrite** — `--optimize` and hard-budget paths propose alternatives → AskQuestion → apply; never silent path rewrite

## Notes

- Selectors and depth: [refs/input-resolution.md](refs/input-resolution.md)
- **Version law (Shared):** `refs/planning/baselines.md` — flow skills only; no skill-local version stubs. Non-loaders: humanize, git helpers, rr-test. Index: `refs/planning/README.md`
- Shared ledger / items / setup: plugin `refs/planning/` (link there directly — no skill stubs)
- Technique refs above are skill-local under `skills/rr-planner/refs/`
- `docs/agent.plan.md` is tripwire only — refuse non-patch; route here or `rr-discovery`
- Lexicon: plugin `GLOSSARY.md` / `ACRONYMS.md` — context budget, DEC, ADR narrowed, spine = constitution
