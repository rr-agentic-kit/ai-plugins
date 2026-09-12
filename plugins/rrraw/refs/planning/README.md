# Shared planning refs

**Single SoT package** for Discover → Plan → (future Execute). Flow skills load these paths directly — **no** `skills/*/refs/baselines.md` (or other version-law) stubs.

| Ref | Role |
|-----|------|
| [baselines.md](baselines.md) | **Version law** — track, docs/product patches, pins, unlock, ship ceremony, rejected patterns |
| [challenge-layers.md](challenge-layers.md) | Challenge tiers, freeze-suggest, risk-accept, solid-subset advance |
| [setup.md](setup.md) | `--setup` bootstrap + **PR-scoped** `validate_planning` wire |
| [output-formats.md](output-formats.md) | Layout, status, handoff YAML shapes |
| [project-lexicon.md](project-lexicon.md) | Host `docs/GLOSSARY.md` + `ACRONYMS.md` silent harvest |
| [agent-config.md](agent-config.md) / [agent.plan.md](agent.plan.md) | Injection + tripwire template |
| [contracts.md](contracts.md) | Task agent contracts |
| [success-criteria.md](success-criteria.md) | Static + judgment gates |
| [decision-ledger.md](decision-ledger.md) | Rationale / evidence ledger |
| [progress.md](progress.md) | Verifying phrases + Next Up / risk-accept close |
| [doc-standards/](doc-standards/) | Item schema (identity — not SemVer) |

Plugin Spec (process-ownership UX): [`INTENT.md`](../../INTENT.md).

## Versioning ownership

**One version law file:** [baselines.md](baselines.md). All **flow** skills load it. Helpers and orthogonal skills must not.

| Consumer | Loads versioning? | Why |
|----------|-------------------|-----|
| **rr-discovery** (flow) | Yes | Freeze, `--change`, open-next, mint |
| **rr-planner** (flow) | Yes | Slice freeze, pins across dirs, open-next |
| **Future Execute** (flow) | Yes | Product ship / track lock; same model — do not invent a third |
| Compose / challenge planning agents | Pins/rev **read-only**; skill mints | Agents do not write `status.yaml` |
| **rr-humanize** | **No** | Prose pass only |
| **Git helpers** (if any) | **No** | VCS ≠ planning SemVer |
| **rr-test** | **No** | Orthogonal quality path |

Rules:

- Flow skill README / SKILL Shared-refs tables name `refs/planning/baselines.md` once (link, don’t restate).
- Helpers must not gain version steps, unlock gates, or mint language.
- `docs/agent.plan.md` is a **tripwire only** — refuse non-patch work; route to a flow skill. Does not classify or mint.
