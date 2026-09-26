# project-posture

**Owner (Plan):** PRD-shape, `arch_doc_mode`, optional interview-mode preference, and legend consumption from a **frozen** Discover posture. Discover owns existence × commitment confirm and `domain_context` mint (`skills/rr-discovery/refs/project-posture.md`).

**Load when:** Plan entry after business-case gate, before minting PRD / standing structure. Resume skips if `prd_shape` already set and uncontradicted.

## Do not re-run Discover posture

If `project_posture.user_confirmed` is missing → **stop** and route to `rr-discovery` (or brownfield AskQuestion). Plan does not invent existence/commitment.

## PRD-shape reflection

Before first PRD compose:

| Field | Values | Done when |
|-------|--------|-----------|
| `prd_shape` | `story_led` \| `feature_led` \| `hybrid` | User-confirmed once |
| `scope_mode` | `discovery` \| `closed` | User-confirmed once |
| `arch_doc_mode` | `constitution-primary` (**prefer**) \| `legacy-combined` (transition only) | User-confirmed once — primary = always-load `constitution.md`; architecture = tech ADRs only. `legacy-combined` = fat architecture still embeds constitution — migrate via `--optimize`, do not mint new combined blobs |
| `interview_mode` | `coach` \| `fast` | Optional; offer once per Plan session ([plan-interview.md](plan-interview.md)) |

Persist on `session_state.project_posture`. Compose/standing layer read these for structure ([prd.md](doc-standards/prd.md), [constitution.md](doc-standards/constitution.md), [architecture.md](doc-standards/architecture.md)).

Legacy values `combined` / `split`: treat `split` as `constitution-primary`; treat `combined` as `legacy-combined` and offer optimize migrate.

## Legend consumption

| Source | Plan use |
|--------|----------|
| BRD MoSCoW (frozen) | Inheritance only — do not re-cut BRD Must |
| PRD RICE/RIC + P1–P3 | Scoring / requirement priority — never MoSCoW on PRD |
| Selection `_status_` | Build-now marker — never a second scope doc |

## Cascade impact (Plan)

| Do | Do not |
|----|--------|
| Run PRD-shape + arch_doc_mode before minting structure | Skip entry gate because posture exists |
| Prefer constitution-primary standing law | Mint new constitution-inside-architecture blobs |
| Cite frozen BRD MoSCoW when inheriting | Apply MoSCoW cut-pass on PRD |
| Park market/viability reopen to Discover | Re-litigate signed BRD Must in Plan |
| Offer Coach/Fast once | Invent sprint / release-plan ceremony this pass |

## Failure modes this blocks

- Composing PRD without confirmed Discover posture / handoff
- Running a PRD MoSCoW cut-pass instead of RICE + P-tags on requirements
- Effort without standing law / dual-lens ([system-design.md](system-design.md))
- Re-opening signed BRD Must as Plan inventiveness
- Misnamed “architecture spine” absorbing product constitution (context bloat)
