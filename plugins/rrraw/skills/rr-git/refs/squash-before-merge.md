# Squash onto a base branch

**When:** Local squash of the current branch onto `origin/main` or `origin/master` (pre-merge on forges without native squash-on-merge, or any repo that wants one commit before merge). GitLab/GitHub squash-on-merge at the forge does **not** need this script. Force-push here is still **pre-forge** squash (rr-git), not PR/MR create.

**Script:** `skills/rr-git/scripts/squash-onto-base.sh` — invoke from [scripts/README.md](../scripts/README.md). Confirm with the user before force-push.

## Platform gate

| Origin | Action |
|--------|--------|
| GitLab or GitHub and user asked for **forge squash-on-merge** | Skip this script; use `glab mr create --squash-before-merge` or GitHub squash merge |
| Forge without native squash-on-merge, or explicit local squash | Run the script |

## Base

`origin/master` then `origin/main`, or `--base`. Never force-push without backup branch + user confirm ([safety.md](safety.md)).

## Script flags (align with scripts/README)

`--verify-only` | `--force-push` `[<source-branch>]`; `--yes`; `--auto-cleanup` / `--no-cleanup`; `--integrate rebase|none`; `--base <branch>`. Env: `BASE_BRANCH`, `OUTPUT_BRANCH`, `COMMIT_MSG`, `COMMIT_SUBJECT`.
