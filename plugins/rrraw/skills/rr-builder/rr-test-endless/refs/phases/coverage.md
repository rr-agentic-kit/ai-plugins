# Phase: coverage gateway (§0)

**Load when:** iteration **`n > 1`** before assess; also referenced by verify toolchain prompt path.

**Skip when:** **`n === 1`** — the **`rr-builder --add-endless-test`** command already ran **`test-endless-toolchain`** with **`build`** + **`test:coverage`**.

## Steps

1. **`Read`** **`PLUGIN_ROOT/skills/rr-builder/rr-test-endless/refs/toolchain-coverage-gateway-prompt.md`**.
2. Build the **`Task`** **`prompt`** from that file’s **text**-fenced block by replacing **`REPO_ROOT`** with the absolute repository root (contents only, no fence lines).
3. **`Task`** — **`subagent_type`:** **`test-endless-toolchain`**, **`description`:** **`Toolchain gateway: build + test:coverage (iteration n)`** (substitute actual **`n`**), **`prompt`:** (substituted block).

On **hard** failure (build or tests did not run per gateway ref) → **STOP** and **Report**.
