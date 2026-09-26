# Inline fix procedure (orchestrator session)

**Purpose:** Orchestrator-owned execute step between manifest triage and verify. **Audience:** **s-refactor** epoch loop — **not** a `Task`.

## Preconditions

- **`epochs/epoch-{NNN}-manifest.json`** exists with triage complete
- At least one item has `auto_fixable: true` and `status: pending` — otherwise skip execute substep
- **`refs/fix-disposition.md`** loaded or already in session

## Procedure

1. **`Read`** **`agents/refactor/fix.md`** once per execute substep (or keep warm from epoch start).
2. **`Read`** **`refs/fix-disposition.md`** if not already loaded.
3. Group pending `auto_fixable: true` items by **`phase`** ascending (**1→8**). Within a phase, process high-priority structural types first (same order as collector).
4. For each phase group:
   - Apply fixes per **`fix-disposition.md`** and fix worker scope rules.
   - Honor **`disposition`** on every item — never auto-apply `escalate_human`.
   - Update manifest item `status` → `executed` or `no_progress` / `clarified` / `escalated` with `reason`.
   - **Compile/build** after each coherent step when project policy requires it.
5. Collect counts: `{fixed, no_progress, escalated, clarified}` and remaining fingerprints.
6. **Persist** updated manifest via **`Write`** before verify.

## Verify + rollback

1. Run project test command (detect from manifests / prior build stage).
2. Run lint/static on **touched files** (Checkstyle/Biome/Spotless when configured).
3. On failure: **rollback** the last coherent edit batch (git checkout of touched paths or manual revert); mark affected manifest items `no_progress` with verify failure reason.
4. On success: mark executed items `verified`.

## Forbidden

- **`Task`** for fix worker — inline only in orchestrator session
- Skipping pending `auto_fixable: true` items without `no_progress` reason
- Applying fixes out of phase order **1→8**
- Claiming epoch complete before manifest + verify artifacts updated

## Handoff back to epoch loop

Return fix counts to orchestrator session; continue to **expand-scope** when verify passed, else **AskQuestion** or **`stopped`** per **`SKILL.md`**.
