# project-posture

**Owner (Plan):** PRD-shape reflection and MoSCoW/RICE legend consumption from a **frozen** Discover posture. Discover owns existence × commitment confirm and `domain_context` mint ([rr-discovery project-posture](../../rr-discovery/refs/project-posture.md)).

**Load when:** Plan entry after business-case gate, before minting PRD structure. Resume skips if `session_state.project_posture.prd_shape` is already set and user has not contradicted it.

## Do not re-run Discover posture

If `project_posture.user_confirmed` is missing → **stop** and route to `rr-discovery` (or brownfield AskQuestion). Plan does not invent existence/commitment.

## PRD-shape reflection (T8-25 / T8-26)

Before first PRD compose:

| Field | Values | Done when |
|-------|--------|-----------|
| `prd_shape` | `story_led` \| `feature_led` \| `hybrid` | User-confirmed once |
| `scope_mode` | `discovery` \| `closed` | User-confirmed once |

Persist on `session_state.project_posture`. Compose reads these for release-phasing prose ([doc-standards/prd.md](doc-standards/prd.md)).

## Legend consumption

| Source | Plan use |
|--------|----------|
| BRD MoSCoW (frozen) | Inheritance only — do not re-cut BRD Must |
| PRD RICE/RIC | Scoring method for PRD leaves — never MoSCoW on PRD |

## Cascade impact (Plan)

| Do | Do not |
|----|--------|
| Run PRD-shape reflection before minting PRD structure | Skip entry gate because posture exists |
| Cite frozen BRD MoSCoW when inheriting | Apply MoSCoW cut-pass on PRD |
| Park market/viability reopen to Discover | Re-litigate signed BRD Must in Plan |

## Failure modes this blocks

- Composing PRD without confirmed Discover posture / handoff
- Running a PRD MoSCoW cut-pass instead of RICE
- Re-opening signed BRD Must as Plan inventiveness
