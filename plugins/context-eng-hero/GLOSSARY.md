# Glossary

| Term | Meaning (this plugin) | Not confused with | Notes |
|------|----------------------|-------------------|-------|
| extract | Action: derive README/spec (or other artifact) from existing definition + provenance | Unzip / unpack an archive | `refs/actions/extract.md` |
| fix | Minimal edits preserving existing intent (audit/test-led) | redesign (outcome/scope change) | Route via classify |
| redesign | Change outcome, audience, capabilities, or contracts | fix (same intent, repair FAILs) | Structural edits allowed |
| audit | Diagnosis-only static + rubric report; no file edits | Write-path gates that run static as a step | Compliance PASS/FAIL; `refs/actions/audit.md` |
| audit-redesign | Diagnosis-only improvement report (Keep/Improve/Restructure opportunities); no file edits | compliance **audit**; redesign action | Shipped action `refs/actions/audit-redesign.md`; close via **post-audit-redesign-routing** |
| opportunity | Ranked improvement finding with evidence, impact, confidence, absorb hint; after challenge + impact×confidence filter | compliance **FAIL** (ship/write blocker) | Stable fields in Ranked table / lean `ranked[]` per `templates/reports/opportunity.schema.json`; `--improve` Tasks emit lean JSON → `render_ce_report.py`; parent merges from rendered md or lean arrays |
| touch list | Newline-separated repo-relative paths an `--improve` run wrote/promoted | Full working-tree dirty set; `git add -A` | Persisted as `.ai/learning/ce-improve/<run-id>/touch-list.txt`; scoped `git add` after Approve only |
| Caller Load | Parent skill/Task injects refs + payload into a plugin agent or parent-only Task executor; executor does not ambient-discover the parent pack | Agent owning its own `refs/` tree; ambient skill discovery | `design/agent.md`; layout picker in `design/design-core.md` |
| shared knowledge layout | Where judgment/templates live: skill `refs/` SoT (parent + its agents/executors), plugin-level `refs/<pack>/` (≥2 skills), or internal sub-skill (orchestrated procedure only) | Dumping rubrics into a sub-skill; `agents/<id>/refs/`; mega-agent modes | Forbidden: agent-private refs trees and mega-agents; see `design/design-core.md` |
| text-mode fallback | Same enumerable options as AskQuestion, delivered as numbered/labeled prose | Claiming AskQuestion is “unavailable” as product truth | `questioning.md` **Delivery channels**; mandatory when tool/harness missing |
| Delivery channels | Contract for how clarify/gate questions reach the user (AskQuestion preferred; text-mode same options mandatory) | Transport/network channels; chat UI chrome alone | `questioning.md`; audit id `*.clarify.delivery-channels` |
| skill UX | Create/design choice of input/delivery interaction shape (gates+reports / text-first / minimal) | Purpose/Procedure content; invoke mode | Gate `skill-ux-delivery`; wires README UX + Orchestration only |
| --improve | Parallel compliance + opportunity audits → merge → absorb under write gates → scoped `git add` of touch list | Running either diagnosis alone; ambient “make it better” without a path; `git commit` from improve | Lean JSON (`templates/reports/<kind>.schema.json`) + validate→Jinja `render_ce_report.py`; executors + Caller Load; action `refs/actions/improve.md` |
| learn | Gap package from a live run miss (patch or friction); no skill edits this action | Study / read documentation | Hands off to fix/redesign; investigation requires layer-split + mechanism-completeness |
| layer-split | Split founder/human corrections into outcome / mechanism / persistence / stop-rule before topic merge | Single collapsed “big picture” topic | `refs/actions/learn.md` effort bar |
| mechanism-completeness | Outcome/north-star `skill_gap` must have a runtime companion (`step`/`stop-rule`/`probe`/`anti-trigger`) | Purpose/README prose alone | Blocks philosophy-only packages |
| adequacy probe | Pre-approve check: would selected-only absorb miss named operational nuance? | Post-hoc human adequacy review | `learn-3-topics` + topics template Checkpoint |
| gate | Write or routing gate (static → reflection → pre-ship → approve) | CI quality gate in general | Shared write gates |
| ref | Progressive-disclosure markdown under `skills/<name>/refs/` | Git ref / reference implementation | One hop from SKILL |
| Skill+Ref | Pack architecture: invariant procedure in SKILL; variants in refs | A skill that merely links docs | Rubric `skill-ref.*` |
| draft-only | Deliver draft in chat; do not write final path | Incomplete WIP on disk | Write gate FAIL outcome |
| eval-first | Author minimum that would pass observed FAIL; thicken later | Front-loaded research phase | Advisory default |
| always-on | `AGENTS.md` (or user-global equivalent) loaded every session — ~90%-leverage only | Situational pack; full project docs | `recipe-static-memory` |
| situational pack | Flat `.agents/{group}.md` depth loaded on Read trigger — never `@`-imported | Cursor `.agents/skills/`; CONTRIBUTING dump | Derive group names; zero packs OK |
| plugin agent | Marketplace catalog Task/subagent under `plugins/<plugin>/agents/**/*.md` (`name` + `description` → Cursor Task types / Claude `@`-mention every session; function-style default; `name` = file stem) | `AGENTS.md` always-on; `.agents/` situational packs; **Task executor** (parent-only skill ref) | Body tool fence required; see `recipe-context-engineer` `refs/design/agent.md` |
| Task executor | Parent-only one-shot executor: skill `refs/executors/<role>.md` (no catalog frontmatter); spawned via `generalPurpose` / generic Agent + Read + Caller Load | Plugin agent file under `agents/` (discovery registration); parent chat skill | Spec loads only when Task runs; exemplar `refs/executors/compliance.md` + `opportunity.md` for `--improve` |
| Task subagent | Runtime-spawned isolated executor (Cursor Task / Claude subagent) that may load a plugin agent **or** a Task executor ref | Plugin agent file itself; parent chat skill | Caller injects Load + payload; `agents/` is not a prerequisite for Task isolation |
| inclusion bar | Keep only constraints that help or prevent mistakes in ~90%+ of chats | “Everything the user asked for”; project bible | Challenge failing requests on design/review/fix |
