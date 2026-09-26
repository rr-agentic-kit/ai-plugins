# Size Thresholds

**Purpose:** Module / test-file counts that classify **small / medium / large** for pre-flight **logging and triage** only. Chunk geometry and work-pack dispatch come from **`chunking.md`** and **`work-pack-sizing.md`** respectively — not this file.

Tunable thresholds for the endless add-test lane.

## Tiers


| Tier   | Module count | Test file count | Behavior (assess fan-out hint) |
| ------ | ------------ | --------------- | ------------------------------ |
| Small  | < 5          | < 50            | Single assess per scope          |
| Medium | 5–15         | 50–150          | Assess per module, aggregate   |
| Large  | > 15         | > 150           | Assess per module, aggregate   |


**Module** = Maven module, npm workspace package, Go package, Python package, Gradle subproject.

**Test file** = file matching test patterns (e.g. `*Test.java`, `*.test.ts`, `*_test.go`, `test_*.py`).

### Stricter tier (module vs test files)

Compute **module tier** and **test file tier** from the tables above. Set **size class** to the **stricter** of the two (the tier that implies more splitting work: Small < Medium < Large). Example: 4 modules but 60 test files → **Medium**.

### Boundary behavior

If a count **equals** a threshold (e.g. exactly **5** modules, **50** test files, **15** modules, **150** test files), use the **stricter** tier on that dimension (the band **at or above** the boundary for “small vs medium” / “medium vs large”). Pre-flight defers here; do not re-encode thresholds outside this file.

---

## Collector (Assessor) Split


| Tier   | Split rule                                                          |
| ------ | ------------------------------------------------------------------- |
| Small  | Single `test-endless-assess` (`STAGE=assess`, `EVAL=test`) for full scope              |
| Medium | Invoke assess subagent per module/path. Aggregate inventory + gaps. |
| Large  | Same as Medium.                                                     |


**Dispatch geometry:** **`skills/s-test-endless/refs/work-pack-sizing.md`** is **canonical** for planner packing and orchestrator **`Task`** dispatch (one worker per plan file). This file does **not** define executor batch sizes or step batching.

---

## Tunable Values

- `SMALL_MODULE_MAX`: 5
- `SMALL_TEST_FILE_MAX`: 50
- `MEDIUM_MODULE_MAX`: 15
- `MEDIUM_TEST_FILE_MAX`: 150
