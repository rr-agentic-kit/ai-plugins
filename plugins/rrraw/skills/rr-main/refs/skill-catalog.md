# rr-main skill catalog

**Audience:** `orient` / `explain`. Public skills only — mirror `plugin.json` `skills[]`. One-liners + when-not + peer path. No Procedure paste.

## Public `rr-*`

| Skill | One-liner | When not | Peer |
|-------|-----------|----------|------|
| `rr-main` | Orient, explain, situate, suggest; confirm before peer handoff | Doing Discover/Plan/Build/CI work | `skills/rr-main/SKILL.md` |
| `rr-discovery` | Freeze ES→MRD→BRD to `business-case.yaml`; setup, resume, challenge, from-code | PRD / RICE / stories / architecture authorship | `skills/rr-discovery/SKILL.md` |
| `rr-planner` | Honest RICE Effort + slice kernel after Discover freeze; PRD, intake, freeze-slice, challenge | Problem/market/viability; coding / `--feature` | `skills/rr-planner/SKILL.md` |
| `rr-builder` | Orchestrate slice build or hand off one lane; intake / feature / adhoc | Cascade planning; forge-only without ship handoff; local-git-only | `skills/rr-builder/SKILL.md` |

## Public `s-*` (builder lanes + ops)

| Skill | One-liner | When not | Peer |
|-------|-----------|----------|------|
| `s-prepare` | Decompose pin-complete execute-slice into `docs/rr/tasks/` | Product Plan / implement | `skills/s-prepare/SKILL.md` |
| `s-coder` | Production implement/refactor standards for scoped change | Test-primary / multi-lane review / CI ship | `skills/s-coder/SKILL.md` |
| `s-tester` | Flag-driven test excellence via `agents/test/*` | Planning docs / version mint | `skills/s-tester/SKILL.md` |
| `s-security` | OWASP audit with confidence gating (report-only) | Auto-fix security findings | `skills/s-security/SKILL.md` |
| `s-review` | Multi-lane review under `.ai/review/<runId>/` | Discover `--challenge`; local git only | `skills/s-review/SKILL.md` |
| `s-refactor` | Fixed-point behavior-invariant coder-rule refactor | Casual cleanup without scoped path set | `skills/s-refactor/SKILL.md` |
| `s-test-endless` | Coverage-first endless test perfection loop | One-shot assess without epoch loop | `skills/s-test-endless/SKILL.md` |
| `s-ci` | Forge router: PR/MR, CI debug, Sonar fix, Dependabot, publish/deploy route | Local git only | `skills/s-ci/SKILL.md` |
| `s-gh` | GitHub PR/issue/Actions patterns (also via s-ci) | GitLab-primary forge work | `skills/s-gh/SKILL.md` |
| `s-glab` | GitLab MR/issue/pipeline patterns (also via s-ci) | GitHub-primary forge work | `skills/s-glab/SKILL.md` |
| `s-publish` | Publish artifacts to Pages, registries, releases, object storage | Deploy cluster/GitOps | `skills/s-publish/SKILL.md` |
| `s-deploy` | Deploy via Helm, Kubernetes, GitOps (Argo CD) | Publish-only artifact push | `skills/s-deploy/SKILL.md` |
| `s-git` | Local git safety, worktrees, rebase, squash, conflicts | PR/MR ship / pipeline debug | `skills/s-git/SKILL.md` |
| `s-humanize` | Humanize docs/MR prose; AI-tell removal | Planning freeze / code implement | `skills/s-humanize/SKILL.md` |

## Catalog rules

- Explain answers cite this table + peer README when depth needed — never load peer `refs/` from rr-main to answer “how”
- Unknown / unlisted name → say not in catalog; nearest peer if obvious
- Nested builder lanes are listed because they appear in `skills[]`; prefer `rr-builder --<lane>` in role-map for engineers

## Anti-patterns

- Do not invent `rr-test` or other absent skills
- Do not copy peer Actions tables wholesale — one-liner + when-not only
