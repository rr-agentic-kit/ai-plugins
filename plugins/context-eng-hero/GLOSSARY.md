# Glossary

| Term | Meaning (this plugin) | Not confused with | Notes |
|------|----------------------|-------------------|-------|
| extract | Action: derive README/spec (or other artifact) from existing definition + provenance | Unzip / unpack an archive | `refs/actions/extract.md` |
| fix | Minimal edits preserving existing intent (audit/test-led) | redesign (outcome/scope change) | Route via classify |
| redesign | Change outcome, audience, capabilities, or contracts | fix (same intent, repair FAILs) | Structural edits allowed |
| audit | Diagnosis-only static + rubric report; no file edits | Write-path gates that run static as a step | `refs/actions/audit.md` |
| learn | Gap package from a live run miss (patch or friction); no skill edits this action | Study / read documentation | Hands off to fix/redesign; investigation requires layer-split + mechanism-completeness |
| layer-split | Split founder/human corrections into outcome / mechanism / persistence / stop-rule before topic merge | Single collapsed “big picture” topic | `refs/actions/learn.md` effort bar |
| mechanism-completeness | Outcome/north-star `skill_gap` must have a runtime companion (`step`/`stop-rule`/`probe`/`anti-trigger`) | Purpose/README prose alone | Blocks philosophy-only packages |
| adequacy probe | Pre-approve check: would selected-only absorb miss named operational nuance? | Post-hoc human adequacy review | `learn-3-topics` + topics template Checkpoint |
| gate | Write or routing gate (static → reflection → pre-ship → approve) | CI quality gate in general | Shared write gates |
| ref | Progressive-disclosure markdown under `skills/<name>/refs/` | Git ref / reference implementation | One hop from SKILL |
| Skill+Ref | Pack architecture: invariant procedure in SKILL; variants in refs | A skill that merely links docs | Rubric `skill-ref.*` |
| draft-only | Deliver draft in chat; do not write final path | Incomplete WIP on disk | Write gate FAIL outcome |
| eval-first | Author minimum that would pass observed FAIL; thicken later | Front-loaded research phase | Advisory default |
