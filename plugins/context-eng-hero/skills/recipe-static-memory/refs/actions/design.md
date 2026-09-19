# Action: design (internal)

**From scratch** project (default) or user-global agent instruction packs.

## Load (Read)

- `memory-hierarchy.md`
- `agents-md-bridge.md`
- `situation-groups.md` (scope `project`, and `user` when packs considered)
- `user-sections-template.md` (scope `user`) or `project-sections-template.md` + `project-init-flow.md` (scope `project`)
- `communication-role-exhaustive.md` (**user** scope only — mandatory)
- `tooling-orchestration.md` (**user** scope only — mandatory unless user waives §6)
- `user-global-synthesis.md` (**user** scope — adaptive buckets)
- `effective-writing.md`

## REQUIRED (command)

- `scope`: `project` (default) | `user` — treat as `project` unless user explicitly names user-global / `~/.claude/`
- Optional explicit path (defaults: project `AGENTS.md` + `CLAUDE.md` pointer; user `~/.claude/CLAUDE.md` / always-on import)

## Stop

If target always-on file exists with meaningful content and user did not confirm rewrite → **Next step (user):** `/static-memory-review` or `/static-memory-fix`.

Challenge requests that fail the 90% inclusion bar—route to docs / skills / packs only when justified per `situation-groups.md`.

## Steps

### Step 1: `1-design-scope`

- **Outcome:** Scope, paths, and scratch intent confirmed.
- **Done when:** `project` (default) vs `user` set; always-on + Claude pointer paths agreed; rewrite confirmed if files exist.

### Step 2: `2-design-gather`

- **Outcome:** All required inputs collected.
- **Done when:**
  - **user:** `communication-role-exhaustive.md` complete for groups **A** and **B** (all dimensions resolved or N/A with reason; checkpoint/resume allowed); then `tooling-orchestration.md` group **C** complete or §6 explicitly waived; then adaptive buckets per `user-global-synthesis.md`
  - **project:** `project-init-flow.md` explore done; stack/commands grounded in repo; inclusion bar applied; situational groups derived only if leftover fails always-on budget; shorter tooling pass per `tooling-orchestration.md` if repo has local plugins/skills

### Step 3: `3-design-draft`

- **Outcome:** Full markdown draft for always-on (+ pointer + optional packs).
- **Done when:** Draft per template leverage (omit empty sections); `CLAUDE.md` thin `@AGENTS.md` for project; packs only if `situation-groups.md` justifies; no `@` of situational packs; comm/role exhaustive for user scope; §6 trigger table when group C done; project omits comm/role unless user insisted; pointers to README/CONTRIBUTING where docs are authoritative.

### Step 4: `4-design-confirm`

- **Outcome:** User-approved draft.
- **Done when:** Full draft shown (always-on + pointer + any packs); user approves or ≤2 revision rounds complete.

### Step 5: `5-design-write`

- **Outcome:** Files written at approved paths only.
- **Done when:** User confirmed write; files saved; suggest `.agents/local.md` in `.gitignore` for project experiments if applicable.

## Write gate (user files)

Not plugin `shared-write-gates.md`. **Confirm-before-write:** no disk write until step 4 passes.

## Output

- Paths written (`AGENTS.md`, `CLAUDE.md`, any `.agents/{group}.md`)
- Sections / packs included (and which were omitted for leverage)
- Import paths if any `@` always-on splits
- Hint: `.gitignore` for `.agents/local.md` when relevant
