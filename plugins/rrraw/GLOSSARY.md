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
| lane | rr-builder handoff class: `prepare` \| `coder` \| `tester` \| `security` \| `review` | Git branch lane; review assess pass (`code`/`test`/`security`) | Nested skill under explicit flag; not orchestrate stage |
| prepare | Builder tech plan: execute-slice → `docs/rr/tasks/` + lazy tech ADRs | Product Plan / rr-planner; implement (rr-coder) | Nested under rr-builder; stop after L3; also orchestrate **prepare** stage |
| auto | rr-builder **drive** (`--auto`): execute without confirm between stages; pairs with `scope` (`next`\|`full`) | Casual “automatic”; CI auto-merge; **orchestrate** mode | Not the same as mode; default drive is **manual**. See [slice-pipeline.md](skills/rr-builder/refs/slice-pipeline.md) |
| manual | rr-builder **drive** (`--manual`): show step(s), wait for confirm/edit (or ready pick), then execute | Casual “by hand”; handoff lane | Default drive; with `full`, ready list marks cursor stage **`(next)`** |
| next (builder) | rr-builder **scope** (`--next`): only the cursor’s next stage | Casual “what’s next”; product next-up | Lone `--next` → `drive=manual`. Cursor stage labeled **`(next)`** in manual-full lists |
| full (builder) | rr-builder **scope** (`--full`): remaining stages until **delivered** (or hard stop) | Review `--scope …\|full`; “full auto” as drive | Default scope; silent multi-stage chain only when `drive=auto` |
| orchestrate | Builder advances slice pipeline (prepare→…→delivered) under drive×scope | Handoff (one nested skill then stop) | Dual-mode invariant with handoff; default `manual` × `full` |
| handoff | Builder loads one nested skill on `--prepare`/`--coder`/`--tester`/`--security`/`--review` and stops | Orchestrate / drive×scope pipeline advance | No silent re-entry to orchestrate in the same run; drive/scope ignored |
| builder_stage | Cursor token on task-summary / `{NNNN}.md`: prepare\|plan\|build\|review\|refactor\|step_validate\|task_validate\|slice_validate\|delivered | Git stage; CI stage metaphor only | With `step_index` + `step_*_done` booleans ([slice-pipeline.md](skills/rr-builder/refs/slice-pipeline.md)) |
| step_plan_done | `{NNNN}.md` boolean: plan done for current `step_index` | Inferring “planned” from prose | Reset to false when advancing `step_index` |
| step_build_done | `{NNNN}.md` boolean: build done for current `step_index` | CI “build passed” | Cursor reads this — not narrative |
| step_review_done | `{NNNN}.md` boolean: review done for current `step_index` | Casual “reviewed” | Orchestrate review sets true after `--fix --all` |
| task-step | Ordered implementer step inside a prepare task’s **Steps** | Full capability atom / prepare task | Pipeline runs plan→build→review→… per step |
| plan (builder) | Task-step stage: enrich step plan + assessment; **plan-knowledge allowlist only**; no app source edits | rr-planner **plan** phase / product Plan | Output shape: [plan-schema.md](skills/rr-builder/refs/plan-schema.md) |
| build (builder) | Task-step stage: implement code + tests via full rr-coder + rr-tester | Generic “build the app”; CI build job | Executes source; after plan done-when |
| review (builder) | Task-step / handoff review: rr-review; orchestrate review forces `--fix --all` | Casual code glance; Challenge (Discover) | Explicit `--review` may be report-only |
| refactor (builder) | Task-step stage **TBD** — skip or stop; do not invent procedure | Ad-hoc cleanup commits | Stub until specified |
| task-validate | Rubric: task Goal / Verify / Obligations met | Slice validate; forge QA | [task-validate.md](skills/rr-builder/refs/task-validate.md) |
| slice validate | Rubric: slice goal / pinned AC met after all tasks PASS | task-validate; product acceptance ceremony | [slice-validate.md](skills/rr-builder/refs/slice-validate.md) |
| delivered | Slice validate PASS — builder stop; ship boundary → **rr-ci** | “Done” chat close without AC proof | Builder does not open PR/MR |
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
