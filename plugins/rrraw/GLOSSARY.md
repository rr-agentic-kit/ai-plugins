# Glossary

| Term | Meaning (this plugin) | Not confused with | Notes |
|------|----------------------|-------------------|-------|
| freeze | Lock a cascade stem or slice as authoritative for handoff | Git freeze / feature freeze ceremony | Discover freeze; Plan slice freeze |
| slice | Buildable Plan kernel (`execute-slice.yaml`) selected for execute | Arbitrary backlog cut / sprint | Pin-complete; prepare then fused code+test |
| spine | Standing **constitution** INDEX (Bind/Prevent/Rule) across features; not fat architecture | Spinal column metaphor; tech ADR catalog | Prefer “constitution”; architecture = tech ADRs only |
| constitution | Always-load standing law (brief + invariant INDEX) | Legal constitution metaphor only | `docs/rr/{track}/plan/constitution.md` |
| decision-lite | Shared Context/Decision/Consequences/Rejections shape | Full ADR ceremony | Product deltas use `DEC-n`; tech uses `ADR-n` |
| context budget | tiktoken soft/hard tiers + detect/optimize for Plan docs | Character count / `wc` | [context-budget.md](skills/rr-planner/refs/context-budget.md); soft≥5k hard≥8k |
| cascade | Ordered ES→MRD→BRD (Discover) or Plan level cycle | Waterfall process | Level todos + compose/humanize |
| challenge | Adversarial review via Task agent — **standard** or **deep** layer | Casual disagreement; smells; auto-reflection; **rr-review Challenge gate** | `--challenge` / `--challenge deep`; [challenge-layers.md](refs/planning/challenge-layers.md) |
| Challenge (review) | rr-review gate that re-triages assess rows before report/fix/ci; consumers use **keep** only | Discover `--challenge` / challenge-layers | Persist `{assess-stem}-challenge.md` under `REVIEW_DIR`; unchallenged challengeable rows stop the report |
| lane | rr-builder work class: `prepare` \| `code` \| `test` \| `security` \| `review` | Git branch lane / swimlane metaphor only | Nested skill or review assess pass |
| prepare | Builder tech plan: execute-slice → `docs/rr/tasks/` + lazy tech ADRs | Product Plan / rr-planner; implement (rr-coder) | Nested under rr-builder; stop after L3 |
| capability atom | Smallest prepare task that delivers observable value (or unlocks it) | Full PRD leaf; pure rename | Grain rubric in rr-prepare |
| task-summary | L1 ordered task list + L3 PR map for one `slice_id` | PRD backlog; sprint board | `docs/rr/tasks/{slice_id}/task-summary.md` |
| global task id | Monotonic integer across slices (`0001.md` …) via `registry.yaml` | Per-slice restarting ids; old `tsk-NNN` naming | Never 0; frontmatter `id:` integer |
| pending_tech | Tech decision topic tracked until forced ADR mint | Product DEC backlog | Listed on task-summary; not pre-persisted ADR dump |
| posture | Prepare sequencing stance vs code/docs: `greenfield` \| `brownfield` \| `docs_ahead` \| `conflict` | Soft “tone” / team culture posture | Classified in rr-prepare; Conflict → stop or AskQuestion |
| doc_drift | Mark on task-summary when brownfield code ahead of Plan/ADRs | Generic docs debt / stale README | Reverse-derive mechanism; do not invent parallel greenfield |
| runId | Daily id for one rr-review run (`yyyymmdd-NN` local) | CI job id / forge pipeline id | Mint: max `NN` for today + 1 (or `01`) |
| REVIEW_DIR | Artifact root `.ai/review/<runId>/` for one review run | `.rr-builder/` (retired); **`.ai/ci/`** (rr-ci sidecars) | Flat locked filenames + merged `report.md` |
| CI_DIR | Sidecar root `.ai/ci/` for rr-ci CLI/skill disk writes | `.ai/review/` (rr-review) | e.g. `job-<id>.log` from `debug-pipeline --save-log` |
| nested skill | Path-loaded child under `skills/rr-builder/` (rr-prepare, rr-coder, …) | Top-level `skills/<name>/` marketplace skill | `name` must equal leaf folder; static matches parent of `SKILL.md` |
| keep | Challenge disposition: row survives for report/fix/POST | Soft demote without Challenge | Consumers must ignore non-keep rows |
| auto-reflection | Continuous phase-transition goal-serve check (no formal report) | User `--challenge`; smells | Standing self-challenge; challenge-layers |
| smells | Always-on fast checkers (req-smell + Discover equivalents) | Challenge attestation / freeze-ready | Smell-clean ≠ freeze-suggest |
| risk-accept | Explicit AskQuestion close of open challenge debt for this digest | Silent skip / “move on” | Stamps `dirty-accepted` |
| solid subset | Cited load-bearing parent facts judged stable enough for work advance | Full parent freeze / pin mint | Work advance OK; mint still needs frozen parent |
| freeze-suggest | Skill may offer freeze as Next Up | User freeze-by-say-so | Requires standard-clear or risk-accept |
| nature | Expectation pack / document nature for compose standards | Natural language / personality | Nature-expectation packs |
| discover | `rr-discovery` phase: ES→MRD→BRD → business-case | General research / exploration | Before PRD |
| plan | `rr-planner` phase: requirements, constitution, slice from frozen case | Project planning ceremony | After Discover freeze |
| from-code | Discover path that extracts stems from codebase evidence | Generic reverse-engineering | `maturity: code-extraction`; no freeze-handoff while extracted |
| beachhead | Narrow market/entry wedge chosen for focus | Military metaphor only | Market framing |
| acceptance | WWAS-shaped AC for a requirement/slice | Generic stakeholder sign-off | Not mere “LGTM” |
| goal-likelihood | Odds that Plan/Build reaches frozen Discover objective / OMTM | Fake percentage / ceremony-complete score | Plan success north-star; freeze is a gate |
| standing self-challenge | Phase-transition auto-reflection: does this step still serve the real goal? | One-shot Gate 2 only / user `--challenge` only | goal-anchor; maps to auto-reflection layer |
| standing red flag | Goal-likelihood risk that resurfaces until founder closes it | Accepted residual / parked note | session_state; Fail freeze if open |
| Discover reopen | Ranked Plan→Discover obligation challenge (wrong Musts / metric drift) | Silent unfreeze / Plan-only HOLD | Route `ask-discover`; backward-chain |
| INTENT | Plugin-level Spec (Why/What/When/Philosophy/UX/Constraints) | Plugin README overview | [INTENT.md](INTENT.md); UX owns process-ownership |
