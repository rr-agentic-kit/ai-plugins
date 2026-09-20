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
| Challenge (review) | rr-review gate that re-triages assess rows before report/fix/ci; consumers use **keep** only | Discover `--challenge` / challenge-layers | Persist `{assess-stem}-challenge.md` under `.ai/review/<runId>/`; unchallenged challengeable rows stop the report |
| lane | rr-builder handoff class: `prepare` \| `coder` \| `tester` \| `security` \| `review` | Git branch lane; review assess pass (`code`/`test`/`security`) | Nested skill under explicit flag; not orchestrate stage |
| prepare | Builder tech plan: execute-slice → `docs/rr/tasks/` + lazy tech ADRs | Product Plan / rr-planner; implement (rr-coder) | Nested under rr-builder; stop after L3; also orchestrate **prepare** stage |
| orchestrate | Builder advances slice pipeline (prepare→…→optional ship→delivered) under drive×scope | Handoff (one nested skill then stop) | Dual-mode invariant with handoff; default `manual` × `full` |
| handoff | Builder loads one nested skill on `--prepare`/`--coder`/`--tester`/`--security`/`--review` and stops | Orchestrate / drive×scope pipeline advance | No silent re-entry to orchestrate in the same run; drive/scope ignored |
| task-step | Ordered implementer step inside a prepare task’s **Steps** | Full capability atom / prepare task | Pipeline runs plan→build→review→validate→optional ship per step |
| plan (builder) | Task-step stage: enrich step plan + assessment (incl. **Ship**); **plan-knowledge allowlist only**; no app source edits | rr-planner **plan** phase / product Plan | Output shape: [plan-schema.md](skills/rr-builder/refs/plan-schema.md) |
| build (builder) | Task-step stage: implement code + tests via full rr-coder + rr-tester | Generic “build the app”; CI build job | Executes source; after plan done-when |
| review (builder) | Task-step / handoff review: rr-review; orchestrate review forces `--fix --all` | Casual code glance; Challenge (Discover) | Explicit `--review` may be report-only |
| delivered | Slice validate PASS — residual ship boundary → **rr-ci** for unshipped work | Mid-slice **ship** stage; “done” chat without AC | Builder does not open PR/MR; planned ships already handed off |
| ship (builder) | Orchestrate stage: resolve plan **Ship** branch/base → hand off **rr-ci** | Forge CLI inside builder; slice **delivered** only | After matching validate when `ship_after` ≠ `never` |
| ship_after | Plan Ship field: `step_validate` \| `task_validate` \| `never` | Always-ship / CI `after_script` | Required on every step plan |
| prior_open_pr | Plan Ship `base`: tip of latest still-open PR in same `pr_group` chain | Always base = default branch | Stacked PRs; fall back to default if none open |
| capability atom | Smallest prepare task that delivers observable value (or unlocks it) | Full PRD leaf; pure rename | Grain rubric in rr-prepare |
| Sonar fix | rr-ci `--fix --sonar`: scripted issue list + agent remediations; no human issue dump | Cursor sonar-list/fix slash skills; CI `code-quality-reports` | Envelope via `sonar-list-issues` |
| pull-dependabot | rr-ci CLI/skill path: merge `origin/dependabot/**` → verify → delete remotes | Renovate onboarding; ad-hoc chat merge loops; Dependabot security alerts | Invoke `--pull-dependabot`; agent only on exit 2 |
| INTENT | Plugin-level Spec (Why/What/When/Philosophy/UX/Constraints) | Plugin README overview | [INTENT.md](INTENT.md); UX owns process-ownership |
| posture | Prepare sequencing stance vs code/docs: `greenfield` \| `brownfield` \| `docs_ahead` \| `conflict` | Soft “tone” / team culture posture | Classified in rr-prepare; Conflict → stop or AskQuestion |
| doc_drift | Mark on task-summary when brownfield code ahead of Plan/ADRs | Generic docs debt / stale README | Reverse-derive mechanism; do not invent parallel greenfield |
| keep | Challenge disposition: row survives for report/fix/POST | Soft demote without Challenge | Consumers must ignore non-keep rows |
| auto-reflection | Continuous phase-transition goal-serve check (no formal report) | User `--challenge`; smells | Standing self-challenge; challenge-layers |
| smells | Always-on fast checkers (req-smell + Discover equivalents) | Challenge attestation / freeze-ready | Smell-clean ≠ freeze-suggest |
| risk-accept | Explicit AskQuestion close of open challenge debt for this digest | Silent skip / “move on” | Stamps `dirty-accepted` |
| solid subset | Cited load-bearing parent facts judged stable enough for work advance | Full parent freeze / pin mint | Work advance OK; mint still needs frozen parent |
| freeze-suggest | Skill may offer freeze as Next Up | User freeze-by-say-so | Requires standard-clear or risk-accept |
| nature | Expectation pack / document nature for compose standards | Natural language / personality | Nature-expectation packs |
| discover | `rr-discovery` phase: ES→MRD→BRD → business-case | General research / exploration | Before PRD |
| plan | `rr-planner` phase: requirements, constitution, slice from frozen case | Project planning ceremony | After Discover freeze |
| beachhead | Narrow market/entry wedge chosen for focus | Military metaphor only | Market framing |
| acceptance | WWAS-shaped AC for a requirement/slice | Generic stakeholder sign-off | Not mere “LGTM” |
| goal-likelihood | Odds that Plan/Build reaches frozen Discover objective / OMTM | Fake percentage / ceremony-complete score | Plan success north-star; freeze is a gate |
| standing self-challenge | Phase-transition auto-reflection: does this step still serve the real goal? | One-shot Gate 2 only / user `--challenge` only | goal-anchor; maps to auto-reflection layer |
| standing red flag | Goal-likelihood risk that resurfaces until founder closes it | Accepted residual / parked note | session_state; Fail freeze if open |
| Discover reopen | Ranked Plan→Discover obligation challenge (wrong Musts / metric drift) | Silent unfreeze / Plan-only HOLD | Route `ask-discover`; backward-chain |
| Sonar fix | rr-ci `--fix --sonar`: scripted issue list + agent remediations; no human issue dump | Cursor sonar-list/fix slash skills; CI `code-quality-reports` | Envelope via `sonar-list-issues` |
| INTENT | Plugin-level Spec (Why/What/When/Philosophy/UX/Constraints) | Plugin README overview | [INTENT.md](INTENT.md); UX owns process-ownership |
