# Phase: assess (§1, §2, §8)

**Load bundle:** assess (see **`orchestration-core.md`**).

## §1 Exhaustive assess (per chunk)

If **`Start: plan`** or **`Start: execute`**, **skip §1** entirely.

Otherwise, for each **`chunk_id`** in order, **invoke `Task`** with **`subagent_type`:** **`test-endless-assess`**, **`prompt`** per **`prompts.md`** / **`leaf-contract.md`**.

After each assessor returns, **Read** the assessment file.

**Aggregate** multi-chunk assessments:

```bash
python3 scripts/endless_test_helpers/cli.py aggregate-counts --assess <path1> [<path2> ...]
```

Stdout: combined **`COUNTS:`** line + merged defect rows (see **`assess-output.md`**). On non-zero exit, **Read** each file and aggregate manually per **`assess-output.md`** § Multi-chunk runs.

**Checkpoint (`assessment_paths_by_chunk`):** When **`Start: fresh`** and §1 ran this iteration, after **all** assessor **`Task`**s succeed, **`Write`**/**merge** checkpoint per **`artifacts.md`** with **`assessment_paths_by_chunk`**.

## §2 Exit check (assess)

If **`Start: execute`**, **skip §2**.

Otherwise apply **exit-conditions.md** to the combined assess model (from §1 or **`Start: plan`** entry slice). If exit → **Report**.

**`Start: plan` entry:** Build combined model via **`aggregate-counts`** on paths from **`assessment_paths_by_chunk`** (or single newest **`tra-*.md`** fallback per **`orchestration.md`** Entry slice).

## §8 Re-assess

Repeat §1 assess prompts with **re-assess** semantics per **`prompts.md`** / **`assess-output.md`** (**`RE-ASSESS DIFF`** when applicable). Optionally store prior assessment path under **`REVIEW_DIR/test/state/`** for diffing.
