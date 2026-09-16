# recipe-context-engineer

Eval-first orchestrator for designing, auditing, fixing, and creating plugin context artifacts.

## Why

Plugin teams ship skills, commands, rules, agents, and workflows that other engineers and agents reuse. Those definitions fail when they are hard to discover, unbounded, or unsafe to edit without gates. This skill exists so authors can harden one scoped artifact at a time—with mechanical checks and judgment rubrics—without turning every session into ambient code review.

**Done when:** A target path has a clear type, a chosen action completed, and (on write paths) static + reflection + pre-ship passed—or the user has an explicit draft-only outcome.

## What

- **Artifact types:** Skill, Skill+Ref, ref file, command, agent, rule, workflow
- **Human spec:** Sibling `README.md` holds Why/What/When; `SKILL.md` holds Procedure (bidirectional per `refs/readme-spec.md`)
- **Lexicon:** Plugin-root `ACRONYMS.md` + `GLOSSARY.md` (always required; harvest on create/design/redesign/extract per `refs/lexicon-spec.md`)

**Out of scope:** Production application code; repo-wide review without a declared artifact path.

### Verification

Mechanical static audit; judgment type rubrics; prompt-based behavior probes.

## Actions

| Action | Outcome | Pick when |
|--------|---------|-----------|
| create | New artifact from template + write gates | New folder or file; no existing definition to extract from |
| extract | Draft + provenance from context | `SKILL.md` exists; user wants README or spec from definition |
| audit | Static + rubric report (no edits) | Check compliance quality without changing files |
| audit-redesign | Ranked Keep/Improve/Restructure opportunities (no edits) | Improvement diagnosis only; no auto-apply |
| improve | Parallel compliance + opportunity audits, then absorb under write gates | Declared path; want diagnose-and-apply (`--improve`) |
| fix | Minimal edits for existing intent | Audit or test FAIL; same outcome and scope |
| redesign | Change outcome/scope + write gates | Wrong capability, audience, or outcome |
| learn | Approved gap package from a live run miss—patch or friction (no skill edits) | Live run miss (patch or friction); fold learning back via fix/redesign |
| test | Behavior probe report | Verify agent behavior against prompts |
| diff | Two-path tradeoff summary | Compare two approaches or paths |
| design | Inline write from classify/clarify | Classify/clarify done; user requests file write this turn |

## When

### Use when

- Picking or narrowing artifact type (including Skill+Ref and ref file)
- Auditing, improving, fixing, creating, extracting, testing, comparing, or learning from a live run miss (patch or friction) on a scoped definition
- Clarifying outcome, audience, and failure modes before authoring
- Generating or updating a skill README from an existing `SKILL.md` (**extract**)
- Packaging gaps after a live run miss (patch or friction) so fix/redesign can absorb without re-deriving the miss (**learn**)

### Avoid when

- Ad-hoc production code review with no artifact path
- Ambient "audit everything" or "improve this skill" without a declared target or live miss
- Repo-wide exploration without a scoped question

## Philosophy

- **Eval-first** — thicken from observed compliance FAILs and ranked improvement opportunities, not anticipated rules
- **Two-level audit** — compliance (`audit`: binary ship/write gate) stays separate from improvement (`audit-redesign`: ranked Keep/Improve/Restructure); `--improve` runs both then applies absorb hints (fix then redesign) under write gates
- **Live-miss → learn → absorb** — diagnose existing skill gaps from a live run miss (patch or friction); fix/redesign folds the handover in
- **Scoped-only** — one declared artifact path per session; never ambient repo review
- **Spec/executor split** — README = human spec; `SKILL.md` = Procedure and action refs
- **Gates-before-write** — static → reflection → pre-ship → approve before any file write

## UX

### Invoke

`disable-model-invocation: true` — start via slash or explicit `Read` of `SKILL.md`; not ambient.

### Intake

Read user message and editor context; route plain requests to classified action via disambiguation and classify refs.

### Clarify

Active **AskQuestion** on path, action, type, invoke mode, and **skill UX (input/delivery)**; one question at a time; use open context before asking. If AskQuestion is missing or rejected, emit the same options as short prose and continue — never stall or claim the tool is “unavailable” (`refs/questioning.md` **Delivery channels**). Create/design: **skill-ux-delivery** gate after invoke mode; choice wires draft UX only—not Purpose/Procedure.

### Output

Stage banners per action; PASS/FAIL evidence tables; draft-only in chat when write gates fail.

### Close

**Next Up** or **AskQuestion** follow-ups; re-enter Act on user choice—no slash deferral.

## Design notes

- **Self-invoke** (`disable-model-invocation`) — orchestrator is expensive; requires explicit invocation
- **Dual close surface** — skill uses AskQuestion; commands may name slash as user homework only
- **STATIC SKIPPED** — audit continues judgment; write paths block until static PASS or user accepts draft-only
- **Minimum draft** — smallest template-shaped draft that satisfies clarify; refs only when FAIL proves the gap
- **audit-redesign + improve** — diagnosis-only `audit-redesign`; `--improve` owns parallel Task audits + gated apply (parent-only executors `refs/executors/compliance.md` + `opportunity.md`; not catalog agents)
- **Question tool fallback** — AskQuestion preferred; text-mode channel mandatory when tool/harness missing (`refs/questioning.md`)

## Constraints

| Topic | Fact |
|-------|------|
| **Invoke** | `disable-model-invocation: true` — slash or explicit `Read` of `SKILL.md` |
| **Eval-first** | Thicken from observed audit/test FAILs—not anticipated rules or mandatory research |
| **Write gates** | Static → pre-write reflection → pre-ship → approve-revise-abort |
| **Paths** | Plugin-relative only; no `..` or absolute paths in authored content |
| **README ↔ SKILL** | README = spec; SKILL = executor. Extract derives README from SKILL constraints, not Procedure paste |
| **Lexicon** | `ACRONYMS.md` + `GLOSSARY.md` at plugin root (or skill sibling if standalone); harvest jargon; empty tables allowed |
| **Skill UX** | Create/design: resolve **skill-ux-delivery**; audit catches lexicon + `*.clarify.delivery-channels` |
| **Clarify caps** | Path unresolvable after 2 AskQuestion rounds → stop; action unresolvable after 1 → default design-assist |
| **Write gate cap** | FAIL after 2 revision cycles → draft-only in chat |

## Notes

- Static audit: `scripts/audit_static.py` from plugin root
- Type rubrics (compliance): `refs/rubrics/`
- Improvement rubric (audit-redesign): `refs/rubrics/audit-redesign.rubric.md`
- Behavior probes: `refs/prompts/`

Executor source of truth: `SKILL.md`. This README is the human spec—not a Procedure echo.
