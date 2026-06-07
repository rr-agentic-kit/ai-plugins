# Action: design (internal)

**From scratch** user-global or project static memory.

## Load (Read)

- `memory-hierarchy.md`
- `user-sections-template.md` (scope `user`) or `project-sections-template.md` + `project-init-flow.md` (scope `project`)
- `communication-role-exhaustive.md` (**user** scope only — mandatory)
- `tooling-orchestration.md` (**user** scope only — mandatory unless user waives §6)
- `user-global-synthesis.md` (**user** scope — adaptive buckets)
- `effective-writing.md`
- `agents-md-bridge.md` (scope `project`)

## REQUIRED (command)

- `scope`: `user` | `project`
- Optional explicit path (default `~/.claude/CLAUDE.md` or cwd `CLAUDE.md` / `.claude/CLAUDE.md`)

## Stop

If target file exists with meaningful content and user did not confirm rewrite → **Next step (user):** `/static-memory-review` or `/static-memory-fix`.

## Steps

### Step 1: `1-design-scope`

- **Outcome:** Scope, path, and scratch intent confirmed.
- **Done when:** `user` vs `project` set; path agreed; rewrite confirmed if file exists.

### Step 2: `2-design-gather`

- **Outcome:** All required inputs collected.
- **Done when:**
  - **user:** `communication-role-exhaustive.md` complete for groups **A** and **B** (all dimensions resolved or N/A with reason; checkpoint/resume allowed); then `tooling-orchestration.md` group **C** complete or §6 explicitly waived; then adaptive buckets per `user-global-synthesis.md`
  - **project:** `project-init-flow.md` explore done; stack/commands grounded in repo; shorter tooling pass per `tooling-orchestration.md` if repo has local plugins/skills

### Step 3: `3-design-draft`

- **Outcome:** Full markdown draft for all template sections.
- **Done when:** Draft in memory per template; comm/role exhaustive for user scope; §6 trigger table when group C done; project omits comm/role unless user insisted.

### Step 4: `4-design-confirm`

- **Outcome:** User-approved draft.
- **Done when:** Full draft shown; user approves or ≤2 revision rounds complete.

### Step 5: `5-design-write`

- **Outcome:** File written at approved path only.
- **Done when:** User confirmed write; file saved; suggest `CLAUDE.local.md` in `.gitignore` for project experiments if applicable.

## Write gate (user files)

Not plugin `shared-write-gates.md`. **Confirm-before-write:** no disk write until step 4 passes.

## Output

- Path written
- Sections included
- Import paths if any `@` splits
- Hint: `.gitignore` for `CLAUDE.local.md` when relevant
