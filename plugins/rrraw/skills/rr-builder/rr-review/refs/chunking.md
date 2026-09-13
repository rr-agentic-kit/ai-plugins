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

## Sort order

Sort chunks by `chunk_id` lexicographically before assess.

## Scope for fix

Each chunk carries **scope prefixes** (repo-relative directories). Inject **CHUNK_SCOPE** block into fix prompts when chunking applies.
