# Git Safety Reference

Detailed command risk analysis and recovery workflows.

## Command Risk Matrix

### Risk Levels

- **CRITICAL**: Can lose work permanently, affects others
- **HIGH**: Can lose work permanently, local only
- **MEDIUM**: Can cause issues but recoverable
- **LOW**: Safe, easily reversible

### Complete Command Risk Table

| Command | Risk | Can Lose Work? | Affects Others? | Recoverable? |
|---------|------|----------------|-----------------|--------------|
| `git reset --hard` | **HIGH** | Yes - uncommitted changes | No | No |
| `git push --force` | **CRITICAL** | Yes - others' commits | Yes | Difficult |
| `git push --force-with-lease` | **MEDIUM** | Conditional | Yes | Difficult |
| `git clean -fd` | **HIGH** | Yes - untracked files | No | No |
| `git branch -D` | **MEDIUM** | Yes - if unmerged | No | Yes (reflog) |
| `git rebase` (local) | **LOW** | No | No | Yes (reflog) |
| `git rebase` (pushed) | **CRITICAL** | Yes - others' work | Yes | Difficult |
| `git checkout -- .` | **HIGH** | Yes - uncommitted changes | No | No |
| `git reset --soft` | **LOW** | No | No | Yes |
| `git reset --mixed` | **LOW** | No | No | Yes |
| `git stash` | **LOW** | No | No | Yes |
| `git commit --amend` (local) | **LOW** | No | No | Yes (reflog) |
| `git commit --amend` (pushed) | **MEDIUM** | Conditional | Yes | Difficult |
| `git merge` | **LOW** | No | No | Yes |
| `git cherry-pick` | **LOW** | No | No | Yes |

## Recovery Workflows

### Scenario 1: Accidentally Ran `git reset --hard`

**Problem**: Lost uncommitted changes.

**Recovery**:
```bash
# Unfortunately, uncommitted changes are gone
# No recovery possible
```

**Prevention**:
```bash
# Always stash before risky operations
git stash
# Now safe to run reset
git reset --hard HEAD~1
# Restore if needed
git stash pop
```

### Scenario 2: Deleted Branch with Unmerged Work

**Problem**: Ran `git branch -D feature-branch` and lost commits.

**Recovery**:
```bash
# Step 1: Find the commit SHA
git reflog
# Look for: "checkout: moving from feature-branch to main"
# Note the SHA before the checkout

# Step 2: Recreate branch
git branch feature-branch <commit-sha>

# Step 3: Verify recovery
git checkout feature-branch
git log
```

**Example reflog output**:
```
a1b2c3d HEAD@{0}: checkout: moving from feature-branch to main
e4f5g6h HEAD@{1}: commit: Add user authentication
i7j8k9l HEAD@{2}: commit: Add login form
```

Recovery: `git branch feature-branch e4f5g6h`

### Scenario 3: Force-Pushed Over Someone's Work

**Problem**: Ran `git push --force` and overwrote teammate's commits.

**Recovery**:
```bash
# Step 1: Communicate immediately with affected team members

# Step 2: Find the overwritten commits
# Ask teammate to run:
git reflog
# Or check remote reflog (if enabled)
git reflog show origin/branch-name

# Step 3: Recover the commits
git fetch origin
git checkout branch-name
git reset --hard <lost-commit-sha>

# Step 4: Merge both histories
git merge <your-commit-sha>

# Step 5: Push the merged result
git push
```

**Prevention**:
```bash
# Use --force-with-lease instead
git push --force-with-lease
# Fails if remote has changes you don't have
```

### Scenario 4: Rebase Went Wrong

**Problem**: Rebase created conflicts or messed up history.

**Recovery**:
```bash
# Abort the rebase
git rebase --abort

# Or if already completed, find previous state
git reflog
# Look for: "rebase: checkout main"
# Note the SHA before rebase started

# Reset to pre-rebase state
git reset --hard <pre-rebase-sha>
```

### Scenario 5: Committed to Wrong Branch

**Problem**: Made commits on main instead of feature branch.

**Recovery**:
```bash
# Step 1: Create branch with current commits
git branch feature-branch

# Step 2: Reset main to before your commits
git checkout main
git reset --hard origin/main

# Step 3: Continue work on feature branch
git checkout feature-branch
```

### Scenario 6: Need to Undo Pushed Commit

**Problem**: Pushed bad commit to remote, others may have pulled.

**Recovery** (safe method):
```bash
# Create reverse commit
git revert <bad-commit-sha>
git push
```

**Recovery** (if no one else pulled):
```bash
# Reset local
git reset --hard HEAD~1

# Force push with lease
git push --force-with-lease
```

### Scenario 7: Accidentally Committed Secrets

**Problem**: Committed API keys or passwords.

**Recovery**:
```bash
# Step 1: Remove from latest commit (if not pushed)
# Edit file to remove secrets
git add .
git commit --amend --no-edit

# Step 2: If already pushed
# Remove secrets from file
git add .
git commit -m "Remove accidentally committed secrets"
git push

# Step 3: CRITICAL - Rotate the exposed secrets
# The secrets are still in git history
# Change passwords, regenerate API keys immediately
```

**Better recovery** (remove from history):
```bash
# Use git-filter-repo or BFG Repo-Cleaner
# This rewrites history - coordinate with team
git filter-repo --path config/secrets.yml --invert-paths
git push --force
```

### Scenario 8: Lost Stashed Changes

**Problem**: Can't find stashed work.

**Recovery**:
```bash
# List all stashes
git stash list

# View stash contents
git stash show -p stash@{0}

# Apply specific stash
git stash apply stash@{2}

# Recover dropped stash
git fsck --unreachable | grep commit
git show <commit-sha>
# If it's your stash, create branch
git branch recovered-stash <commit-sha>
```

## Force Push Decision Tree

```
Need to push after rebase/amend?
├─ Is this a shared branch?
│  ├─ Yes → Don't force push
│  │       → Create new commits instead
│  │       → Or coordinate with team first
│  └─ No → Is it pushed to remote?
│         ├─ Yes → Use --force-with-lease
│         │       git push --force-with-lease
│         └─ No → Regular push is fine
│                git push
```

## Rebase Decision Tree

```
Want to rebase?
├─ Has this branch been pushed?
│  ├─ No → Safe to rebase
│  │      git rebase main
│  └─ Yes → Does anyone else work on this branch?
│           ├─ Yes → Don't rebase
│           │       → Use merge instead
│           │       git merge main
│           └─ No → Safe to rebase
│                  → But requires force-push
│                  git rebase main
│                  git push --force-with-lease
```

## Reflog: Your Safety Net

The reflog records every change to HEAD. It's your recovery tool.

**View reflog**:
```bash
git reflog
```

**Common reflog entries**:
- `commit`: Made a commit
- `checkout`: Switched branches
- `reset`: Ran git reset
- `rebase`: Performed rebase
- `merge`: Merged branches

**Reflog expires**: Entries are kept for 90 days by default.

**Recovery pattern**:
```bash
# 1. Find the state you want
git reflog

# 2. Create branch or reset
git branch recovery <sha>
# Or
git reset --hard <sha>
```

## Pre-Operation Checklist

Before running any destructive command, verify:

- [ ] Do I have uncommitted changes? → `git status`
- [ ] Should I stash first? → `git stash`
- [ ] Is this a shared branch? → Check with team
- [ ] Have I created a backup? → `git branch backup`
- [ ] Do I understand what will be lost? → Review command docs
- [ ] Can I recover if this goes wrong? → Check reflog availability

## Emergency Recovery Commands

**Quick reference for panic situations**:

```bash
# See what you just did
git reflog

# Undo last operation
git reset --hard HEAD@{1}

# Find lost commits
git fsck --lost-found

# Recover deleted branch
git branch recovered <commit-sha>

# Abort current operation
git rebase --abort
git merge --abort
git cherry-pick --abort

# Save everything immediately
git stash save "EMERGENCY BACKUP"
```

## When to Ask for Help

Stop and ask for help if:
- You've lost commits and can't find them in reflog
- Force push affected others and you're not sure how to recover
- Rebase created complex conflicts you don't understand
- You've exposed secrets and need to clean history
- Multiple people are affected by your mistake

**Don't**: Keep trying random commands hoping to fix it.
**Do**: Stop, document what happened, ask for help.

## Related workflows (detailed refs — do not duplicate here)

| Workflow | Ref |
|----------|-----|
| Local squash onto base | [squash-before-merge.md](squash-before-merge.md) |
| Prune merged local branches | [clean-local-branches.md](clean-local-branches.md) |

Both require explicit user confirm before history-rewriting deletes; see each ref for gates and scripts.
