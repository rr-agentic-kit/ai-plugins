# Phase: verify + budget exit (§7, §9)

**Load bundle:** verify (see **`orchestration-core.md`**).

## §7 Verify

From **`REPO_ROOT`**: **`Task`** **`test-endless-toolchain`** — phases **`build`**, **`test`** only. **FAIL** → record; **Report** or re-assess per **exit-conditions.md**.

On **PASS**: optionally update checkpoint **`last_verify_head_sha`** + **`updated_at`** per **`artifacts.md`**.

## §9 Exit check (re-assess)

Apply **exit-conditions.md** after §8 re-assess. Exit → **Report**; else if **`n < max_epochs`** → **`n ← n + 1`**, go to **§0** (**`phases/coverage.md`**); else **Report** (budget exhausted).
