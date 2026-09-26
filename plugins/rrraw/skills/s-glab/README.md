# s-ci / GitLab

GitLab nested skill. Loaded by **s-ci** only after `detect-remote` returns `gitlab`. Not plugin-listed. Runtime: [SKILL.md](SKILL.md).

## Why

Keep GitLab-only `glab`/MCP and `.gitlab-ci.yml` patterns out of the forge-agnostic root while sharing the same `s-ci` CLI surface.

## What

Routes MR upsert (create if missing, update if exists), pipeline debug, inline threads, CI quality/security reports, and pre-merge checks through **glab** or GitLab MCP.

**Out of scope:** GitHub/`gh`, local-only git, publish/deploy mechanics (siblings), inventing `s-ci` subcommands.

## When

### Use when

- Parent s-ci selected GitLab and the task is MR, pipeline, or review work

### Avoid when

- GitHub remotes → sibling `github`
- Local git without an MR → `s-git`
- Pages/registry → sibling `publish`; Helm/K8s/Argo → sibling `deployment`

## Constraints

- `disable-model-invocation` — load by path from parent only
- Do not invent `glab` flags or `s-ci` subcommands — parent `SCRIPTS-SPEC.md`
- Inline / `new_line` rules: [refs/inline-comments.md](refs/inline-comments.md)
- Default MR ship flags: SKILL **Default MR ship** (not duplicated in [refs/cli.md](refs/cli.md))

## Notes

```
gitlab/
├── SKILL.md
├── README.md
└── refs/   # cli, inline-comments, mcp, pipeline-*, mr-resolve, …
```
