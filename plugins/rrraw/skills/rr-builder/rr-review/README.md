# rr-review

Multi-lane review hub for **rr-builder**. Writes artifacts to **`.rr-builder/<runId>/`**.

## Flags

See [refs/params.md](refs/params.md):

```
[--code] [--test] [--security] [--all] [--fix | --ci] [--scope MR|PR|all|full] [paths…]
```

## Flow

brief → chunk → assess (nested lane skills) → Challenge → report | fix | ci

## `--ci` handoff

After Challenge, load **rr-ci** for forge-specific inline POST and pipeline security — review does not embed glab/gh scripts.

## Lane skills

| Lane | Skill |
|------|-------|
| code | `rr-coder/` |
| test | `rr-tester/` |
| security | `rr-security-auditor/` |
