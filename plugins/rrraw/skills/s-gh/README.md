# s-ci / GitHub

GitHub nested skill. Loaded by **s-ci** only after `detect-remote` returns `github`. Not plugin-listed. Runtime: [SKILL.md](SKILL.md).

## Why

Keep GitHub-only `gh`/MCP and Actions patterns out of the forge-agnostic root while still sharing the same `s-ci` CLI command names.

## What

Routes PR upsert (create if missing, update if exists), Actions debug, inline review comments, security/quality reports, and pre-merge checks through **gh** or GitHub MCP.

**Out of scope:** GitLab/`glab`, local-only git, publish/deploy mechanics (siblings), inventing `s-ci` subcommands.

## When

### Use when

- Parent s-ci selected GitHub and the task is PR, Actions, or review work

### Avoid when

- GitLab remotes → sibling `gitlab`
- Local git without a PR → `s-git`
- Pages/releases/packages → sibling `publish`; Helm/K8s/Argo → sibling `deployment`

## Constraints

- `disable-model-invocation` — load by path from parent only
- Do not invent `gh` flags or `s-ci` subcommands — parent `SCRIPTS-SPEC.md`
- Inline comment rules: [refs/inline-comments.md](refs/inline-comments.md)

## Notes

```
github/
├── SKILL.md
├── README.md
└── refs/   # cli, inline-comments, mcp, workflow-rules
```
