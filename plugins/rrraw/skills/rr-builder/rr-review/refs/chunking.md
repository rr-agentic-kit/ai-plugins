# Chunking thresholds (polyglot)

**Purpose:** Deterministic **`chunk_id`** boundaries for large repos so assess scopes stay bounded.

Used by **rr-review** step 4. Same snapshot → same chunk list.

## Tunable constants

| Constant | Default | Meaning |
|----------|---------|---------|
| `SINGLE_ROOT_SOURCE_FILE_THRESHOLD` | **80** | At or above → multiple chunks for that package |
| `MAX_FILES_PER_FLAT_CHUNK` | **40** | Flat layout max files per slice |
| `OVERSIZED_SUBDIR_THRESHOLD` | **100** | Subdivide large child dirs |

## Package root discovery

Discover roots from build manifests:

| Signals | Root |
|---------|------|
| `pom.xml` (Maven) | module directory |
| `package.json` workspaces | each workspace package |
| `go.mod` | module root |
| `Cargo.toml` workspace | each member |
| Single app, no workspace | `.` |

## Primary source tree

| Signals under root `R` | Primary tree |
|------------------------|--------------|
| `src/main/java` | `src/main/java` |
| `src/main/kotlin` | `src/main/kotlin` |
| `src` | `src` |
| `lib` (no `src`) | `lib` |
| Else | `R` |

## Countable files

Production source extensions: `.java`, `.kt`, `.kts`, `.ts`, `.tsx`, `.js`, `.jsx`, `.py`, `.go` (exclude `*_test.go`), `.rs`, `.cs`.

**Skip dirs:** `node_modules`, `dist`, `build`, `coverage`, `.git`, `target`, `__pycache__`, `.venv`, `vendor`, `bin`, `obj`.

## Chunk identity

- Multi-root: one chunk per root.
- Single-root, small: one chunk; `chunk_id` = `R`.
- Single-root, large: one chunk per slice; flat batches use `__tr_<NN>` suffix.

## Chunking algorithm (canonical — numbered)

Deterministic walk from primary source tree `T` down to `chunk_id` list. Same repo snapshot → same chunks.

1. **Count** countable files directly under each immediate child directory of `T` (non-recursive per child; recurse only to total each child's subtree).
2. **Root-level check:** if total countable files under `T` < `SINGLE_ROOT_SOURCE_FILE_THRESHOLD` (80) → single chunk, `chunk_id = T`. Stop.
3. **Else, walk `T`'s immediate child directories** in lexicographic order. For each child `C` with count `n_C`:
   - `n_C ≥ OVERSIZED_SUBDIR_THRESHOLD` (100) → subdivide `C` recursively (repeat step 3 one level deeper inside `C`); each resulting slice is its own `chunk_id = C/<grandchild>`.
   - `n_C` between `MAX_FILES_PER_FLAT_CHUNK` (40) and `OVERSIZED_SUBDIR_THRESHOLD` → one chunk, `chunk_id = C` (whole subtree, not further split).
   - `n_C < MAX_FILES_PER_FLAT_CHUNK` → **merge-bin**: accumulate `C` into a running "misc" bucket for its parent level, in walk order, until the bucket would exceed `MAX_FILES_PER_FLAT_CHUNK`; then close the bucket as one chunk (`chunk_id = <parent>/misc-<NN>`) and start a new bucket. Flush the final bucket as a chunk even if under `MAX_FILES_PER_FLAT_CHUNK`.
4. **Files directly under `T`** (not in any child directory) join the first misc bucket at that level (create one if none open).
5. **Emit** the resulting `chunk_id` list with each chunk's `path_prefixes` (the directories/files it covers). No chunk may be empty; no file may appear in two chunks.

## Sort order

Sort chunks by `chunk_id` lexicographically before assess.

## Scope for fix

Each chunk carries **scope prefixes** (repo-relative directories). Inject **CHUNK_SCOPE** block into fix prompts when chunking applies.
