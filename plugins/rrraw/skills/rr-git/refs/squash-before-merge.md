# Squash onto a base branch

**When:** Local squash of the current branch onto `origin/main` or `origin/master` (Bitbucket pre-merge, or any repo that wants one commit before merge). GitLab/GitHub squash-on-merge at the forge does **not** need this script.

**Script:** `skills/rr-git/scripts/squash-onto-base.sh` (rrraw plugin root). Confirm with the user before force-push.

## Platform gate

| Origin | Action |
|--------|--------|
| GitLab or GitHub and user asked for **forge squash-on-merge** | Skip this script; use `glab mr create --squash-before-merge` or GitHub squash merge |
| Bitbucket or explicit local squash | Run the script |

## Base

`origin/master` then `origin/main`, or `--base`. Never force-push without backup branch + user confirm ([safety.md](safety.md)).
