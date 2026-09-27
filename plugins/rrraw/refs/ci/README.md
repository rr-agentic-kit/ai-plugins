# Shared CI policy refs

**Single SoT package** for forge-agnostic CI/ship agent policy. **s-ci**, **s-gh**, and **s-glab** load these paths directly — no `gh`/`glab` flags or script invoke detail here.

| Ref | Role |
|-----|------|
| [task-shapes.md](task-shapes.md) | Invoke shapes, TodoWrite ids, draft / fix / sonar / issue / ship |
| [pr-mr-templates.md](pr-mr-templates.md) | PR/MR title + description authoring |
| [review-comment-triage.md](review-comment-triage.md) | Review thread disposition |
| [pull-dependabot.md](pull-dependabot.md) | Dependabot remote batch-merge policy |
| [sonar-fix.md](sonar-fix.md) | Sonar remediation procedure |
| [fix/pipeline-fix.md](fix/pipeline-fix.md) | Pipeline fix intake → verify (no forge CLI) |
| [fix/pipeline-fix-rules.md](fix/pipeline-fix-rules.md) | Evidence-gated weakening; forbidden bypasses |

**Out of this tree:** `skills/s-ci/scripts/`, `skills/s-ci/SCRIPTS-SPEC.md` — implementation stays with the s-ci CLI; forge skills link in apply rows only.

## Consumers

| Skill | Role |
|-------|------|
| **s-ci** | Router: detect forge, classify shape, load `refs/ci/**`, delegate apply |
| **s-gh** | GitHub apply: `gh`, Actions, task rows + `skills/s-gh/refs/` + scripts |
| **s-glab** | GitLab apply: `glab`, pipelines, task rows + `skills/s-glab/refs/` |
| **s-publish** / **s-deploy** | Ship-adjacent; load templates when referenced |

Plugin Spec (process-ownership UX): `INTENT.md` at plugin root.
