# Glossary

| Term | Meaning (this plugin) | Not confused with | Notes |
|------|----------------------|-------------------|-------|
| extract | Action: derive README/spec (or other artifact) from existing definition + provenance | Unzip / unpack an archive | `refs/actions/extract.md` |
| fix | Minimal edits preserving existing intent (audit/test-led) | redesign (outcome/scope change) | Route via classify |
| redesign | Change outcome, audience, capabilities, or contracts | fix (same intent, repair FAILs) | Structural edits allowed |
| audit | Diagnosis-only static + rubric report; no file edits | Write-path gates that run static as a step | Compliance PASS/FAIL; `refs/actions/audit.md` |
| audit-redesign | Diagnosis-only improvement report (Keep/Improve/Restructure opportunities); no file edits | compliance **audit**; redesign action | Rubrics SoT; action stub `refs/actions/audit-redesign.md`; wiring deferred |
| opportunity | Ranked improvement finding with evidence, impact, confidence, absorb hint; after challenge + impact×confidence filter | compliance **FAIL** (ship/write blocker) | Unbounded `1…N`; Deferred for medium+hypothesized; see `rubrics/audit-redesign.rubric.md` + `improvement-patterns.md` |
| text-mode fallback | Same enumerable options as AskQuestion, delivered as numbered/labeled prose | Claiming AskQuestion is “unavailable” as product truth | `questioning.md` **Delivery channels**; mandatory when tool/harness missing |
| Delivery channels | Contract for how clarify/gate questions reach the user (AskQuestion preferred; text-mode same options mandatory) | Transport/network channels; chat UI chrome alone | `questioning.md`; audit id `*.clarify.delivery-channels` |
| skill UX | Create/design choice of input/delivery interaction shape (gates+reports / text-first / minimal) | Purpose/Procedure content; invoke mode | Gate `skill-ux-delivery`; wires README UX + Orchestration only |
| --optimize | Reserved future alias: compliance audit → audit-redesign → apply absorb hints (fix then redesign) under write gates | Running either diagnosis alone; ambient “make it better” | Not shipped; keep opportunity ids/template stable |
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
| plugin agent | Marketplace Task/subagent definition under `plugins/<plugin>/agents/**/*.md` (function-style default; `name` = file stem) | `AGENTS.md` always-on; `.agents/` situational packs; ad-hoc Cursor Task without a shipped markdown | Body tool fence required; see `recipe-context-engineer` `refs/design/agent.md` |
| Task subagent | Runtime-spawned isolated executor (Cursor Task / Claude subagent) that may load a plugin agent markdown | Plugin agent file itself; parent chat skill | Caller injects Load + payload |
| inclusion bar | Keep only constraints that help or prevent mistakes in ~90%+ of chats | “Everything the user asked for”; project bible | Challenge failing requests on design/review/fix |
