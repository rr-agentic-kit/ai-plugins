# Job Seeker (jobseeker)

**Version:** 0.0.2  
**License:** Unlicense (see repo root `LICENSE`)

Master and tailor **resumes** and **cover letters** for senior+ Software Engineer, AI Engineer, and ML Engineer roles — with hard-stop integrity gates before every write.

## Skill

| Skill | Path | Role |
|-------|------|------|
| **recipe-resume-coach** | `skills/recipe-resume-coach/SKILL.md` | Orchestrator: intake → workflow → gates → confirm-before-write |

### Workflows

| Intent | Workflow ref |
|--------|--------------|
| Build or expand master resume | `refs/workflows/master-resume.md` |
| Tailor resume to a JD | `refs/workflows/tailor-resume.md` |
| Build master cover letter components | `refs/workflows/master-cover.md` |
| Tailor cover letter | `refs/workflows/tailor-cover.md` |
| Full application (resume + cover) | `refs/workflows/full-application.md` |

### Career directory

Artifacts save to `~/career/` per `refs/file-paths.md`. Master documents are never sent to employers; tailored exports are.

### Integrity contract

- **Never fabricate** metrics, skills, or experience
- All 6 gates in `refs/gates.md` must PASS before write
- User confirms every metric is interview-defensible

## Install

### Cursor

1. Ensure the **ai-plugins** marketplace is added at the repository root.
2. Install plugin **jobseeker** (Job Seeker) from that marketplace.

### Claude Code

1. `/plugin marketplace add <repo-root-url-or-path>`
2. `/plugin install jobseeker@ai-plugins`

### Local plugin dir (Claude Code)

```bash
claude --plugin-dir ./plugins/jobseeker
```

(Run from the **ai-plugins** repo root, or pass an absolute path to `plugins/jobseeker`.)

## Manifests

- Cursor: `.cursor-plugin/plugin.json`
- Claude Code: `.claude-plugin/plugin.json`

Both use `name: jobseeker` matching the directory name under `plugins/`.
