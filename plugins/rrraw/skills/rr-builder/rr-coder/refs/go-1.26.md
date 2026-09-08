# Go 1.26+ Standards (CLI-first)

Authoritative **1.26-only** toolchain and API facts: [Go 1.26 release notes](https://go.dev/doc/go1.26).

Do not claim 1.26 behavior beyond what those release notes document.

## Version / toolchain

- Set `go 1.26` (or newer patch) in `go.mod` when the codebase **intentionally** targets 1.26 APIs and semantics.
- **Older `go` directive:** do not use 1.26-only syntax or stdlib APIs introduced in 1.26 without bumping the `go` line first; keep edits compatible with the module’s declared version.
- Use `toolchain` in `go.mod` only when builds must pin a newer compiler for reproducibility; avoid accidental downgrades of the declared `go` version.
- Per release notes, `go mod init` with toolchain `1.N.X` defaults new modules to `go 1.(N-1).0` — adjust with `go get go@version` when the module must track a specific language version.

## Go 1.26 — use / know (from release notes)

- **`new` with value operands** — `new(expr)` sets the allocated variable’s initial value (e.g. optional pointer fields with `encoding/json`).
- **Generics** — a generic type may refer to itself in its type parameter list (recursive constraints like `Adder[A Adder[A]]`).
- **`go fix`** — rewritten as the home of **modernizers** (many fixers + optional `//go:fix inline` per docs); obsolete historical fixers removed.
- **`go doc`** — replaces removed `cmd/doc` / `go tool doc` (same flags/behavior as noted in release notes).
- **Stdlib** — new [`crypto/hpke`](https://go.dev/pkg/crypto/hpke) (RFC 9180, PQ-hybrid KEMs); new [`testing/cryptotest`](https://go.dev/pkg/testing/cryptotest) for deterministic crypto tests (e.g. where `crypto/dsa` / `crypto/ecdh` now ignore caller-supplied `rand`); new `crypto.Encapsulator` / `crypto.Decapsulator` interfaces.
- **Runtime** — Green Tea GC on by default (release notes cite ~10–40% GC overhead reduction in GC-heavy programs); optional `GOEXPERIMENT=nogreenteagc` until 1.27 per notes.
- **Experimental** — `simd/archsimd` (`GOEXPERIMENT=simd`), `runtime/secret` (`GOEXPERIMENT=runtimesecret`), goroutine leak profile (`GOEXPERIMENT=goroutineleakprofile`); treat as non-stable API unless product policy says otherwise.

## Principles baseline

Load [`refs/code.principles.md`](code.principles.md) for cross-language rules. Idiomatic Go patterns (errors, `context`, structure) live there and in [Effective Go](https://go.dev/doc/effective_go); this file adds **1.26 facts** and **CLI / tooling** deltas in the sections below.

## CLI contract (normative)

- Prefer **stdlib** `flag` / `flag.FlagSet`; stable flag names; wire `-h` / help via `flag.Usage` or explicit help flags; document env overrides and **precedence (env vs flag)** in `Usage`.
- **I/O contract:** **Diagnostics** (logs, human-readable text, progress) → **stderr**; **machine-readable** output → **stdout**. Use `log/slog` on stderr with structured fields for operational diagnostics; do not use `log.Print` / `fmt.Println` for that. Keep short user-facing messages separate from structured fields; never put secrets in upstream-visible errors.
- **Exit codes:** `0` success; `1` usage/config; `2+` operational errors as documented (stable across releases).
- **CLI frameworks:** add **Cobra** or **urfave/cli** only when subcommands, plugin-style commands, or shell completion clearly exceed `flag` ergonomics; vet maintenance/supply chain; keep `go.sum` committed; run `go test ./...` in CI.

## Security (CLI-relevant)

- User paths: `filepath.Clean`, reject `..` and absolute paths when the spec requires a subdir of cwd; validate before `os.Open`, `os.WriteFile`, archive extract.
- Subprocess: no shell unless unavoidable; fixed argv; copy or whitelist env; set `Dir` explicitly when relevant.
- HTTP clients: TLS defaults on; pin timeouts; no `InsecureSkipVerify` in production.
- Use `crypto/rand` for anything security-sensitive; when touching KEM/HPKE or ML-KEM paths, prefer stdlib over ad hoc constructions.

## Testing

- Table-driven tests; use `t.Context()` where cancellation/deadline behavior is under test (Go 1.24+).
- Golden files under `testdata/` when CLI stdout/stderr is a compatibility contract; normalize volatile fields if needed.

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| `run(ctx context.Context) error` from `main` with mapped exit codes | Large `main` with business logic |
| `flag` / `FlagSet` for simple CLIs | Cobra/urfave for single-command tools |
| Context deadlines on outbound calls | Background goroutines without cancellation |
| `go test ./...` + committed `go.sum` | New modules without version policy |
| Table-driven tests + `testdata/` goldens | Snapshot tests coupled to unstable ordering |
| `go fix` modernizers when adopting new idioms | Hand-editing large mechanical migrations |

## Logging / Diagnostics

| Prefer | Avoid |
|--------|-------|
| Structured `slog` (or project logger) with attrs | `fmt.Println` / free-form-only as app logging |
| Redact secrets, tokens, PII from log attrs | Passwords, tokens, raw PII in log values |
| Context-aware correlation when the stack already propagates trace/request ids | Inventing ad-hoc ids; unbounded ids as metric label keys |

Cross-language Prefer/Avoid, disposition, **CP028**–**CP030**: [`observability.md`](observability.md).

## Cross-reference

- Pair with `code.principles.md` and `compliance-rubric.md` on every review (`CPNNN` mapping per compliance-rubric.md).
- Observability findings: [`observability.md`](observability.md) (**CP028**–**CP030**).