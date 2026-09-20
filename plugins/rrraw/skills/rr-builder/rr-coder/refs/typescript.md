# TypeScript Standards (5.7+ / 6.x)

## Version
TypeScript 5.7+ with `strict: true`. Target ES2022+. Treat **6.x** as current when the project already pins it.

## tsconfig Essentials

```json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "skipLibCheck": true,
    "types": ["node"]
  }
}
```

`moduleResolution: "node"` + `module: "ESNext"` causes infinite compilation hang — always use `"bundler"` or `"nodenext"`.

**TS 6.x `types`:** Default is an **empty** `types` array — `@types/*` is no longer auto-included. If Node globals (`process`, `Buffer`, `__dirname`) are needed, set `"types": ["node"]` (and keep `@types/node` as a **devDependency** aligned with the project’s Node major). Use the project package manager (`pnpm` / `npm` / `yarn` per lockfile)—do not invent a different one from IDE hints.

### Root / tooling configs in `include`

Framework-generated tsconfigs (e.g. SvelteKit `.svelte-kit/tsconfig.json`) often list `src/**` and `vite.config.*` only. Root tooling files (`drizzle.config.ts`, Playwright under `config/`, scripts as `.ts`) are **outside** that `include` → IDE reports `Cannot find name 'process'` even when `@types/node` and `types: ["node"]` are correct.

**Prefer:** extend the app `tsconfig.json` `include` to list those files (mirror the generated include paths; paths are relative to the extending config). **Alt:** `import { env } from 'node:process'` (or `/// <reference types="node" />`) when keeping the file outside the project is intentional.

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| Discriminated unions | Optional fields for variant states |
| `satisfies` for config objects | Type annotation that loses literal types |
| `as const` for immutable literals | Mutable config objects |
| `??` (nullish coalescing) | `\|\|` for defaults (treats `0`, `''`, `false` as falsy) |
| `unknown` in catch blocks | `any` or untyped `catch (e)` |
| `import type { Foo }` | Value imports for type-only usage |
| Explicit path mappings in `paths` | Wildcard `"*": ["./*"]` (infinite resolution loop) |
| `NoInfer<T>` on secondary generics | Letting TS widen from all arguments |
| Exhaustive switch with `never` default | Switch without exhaustiveness check |
| Branded types for domain IDs | Raw `string` for different ID types |
| `Promise.allSettled` for independent ops | `Promise.all` when partial failure is acceptable |
| Direct module imports | Barrel `index.ts` re-exports (`export *`) |
| Least-necessary visibility (no `export` / `#`/`private` before export) per [§ Visibility](code.principles.md#visibility--encapsulation) (**CP030**) | Default `export` for module-local helpers |
| Result type (`{ ok, value/error }`) | Throwing for expected failure paths |
| `readonly` on arrays/tuples in APIs | Mutable array params that get mutated |
| `replaceAll` for string replacement | `replace` (replaces first match only; easy to miss) |
| Optional chaining (`?.`) for nullable access | `obj && obj.trim()` or `obj && obj.prop` (S6582) |
| `RegExp.exec(str)` for single-match extraction | `str.match(regex)` when regex has no `g` flag (S6594) |

## Type Safety Patterns

### Discriminated Unions

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };
```

Compiler enforces exhaustive handling. Never use optional fields for variant states.

### Branded Types

```typescript
declare const __brand: unique symbol;
type Brand<T, B> = T & { [__brand]: B };

type UserId = Brand<string, 'UserId'>;
type OrderId = Brand<string, 'OrderId'>;

function userId(id: string): UserId { return id as UserId; }
```

Prevents mixing domain primitives. Use for IDs, sanitized strings, validated inputs.

### Exhaustive Switch

```typescript
function assertNever(x: never): never {
  throw new Error(`Unhandled: ${x}`);
}

switch (status) {
  case 'pending': return handlePending();
  case 'done': return handleDone();
  default: assertNever(status);
}
```

Adding a new union member forces compile errors at every switch.

### `satisfies` + `as const`

```typescript
const routes = {
  home: '/',
  users: '/users',
} as const satisfies Record<string, string>;
// Keys validated, values preserved as literal types
```

## Error Handling

### Result Pattern Over Exceptions

```typescript
type ApiError =
  | { code: 'NOT_FOUND'; message: string }
  | { code: 'VALIDATION'; message: string; fields: Record<string, string> };

type ApiResult<T> = Result<T, ApiError>;

async function fetchUser(id: UserId): Promise<ApiResult<User>> {
  // Return { ok: false, error } instead of throwing
}
```

Reserve `throw` for programmer errors (bugs). Use Result for expected failures (not found, validation, auth).

### Catch Blocks

```typescript
catch (error: unknown) {
  if (error instanceof Error) {
    log(error.message);
  } else {
    log(String(error));
  }
}
```

## Async Patterns

- `Promise.allSettled` when operations are independent and partial failure is OK
- `Promise.all` only when all-or-nothing semantics are required
- `AbortController` + `signal` for cancellable operations and timeouts
- `using` keyword (TS 5.2+) for disposable resources: `using handle = getResource()`

```typescript
async function fetchWithTimeout(url: string, ms: number): Promise<Response> {
  using controller = new AbortController();
  const id = setTimeout(() => controller.abort(), ms);
  try {
    return await fetch(url, { signal: controller.signal });
  } finally {
    clearTimeout(id);
  }
}
```

## Module Patterns

- Use explicit `paths` in tsconfig — never wildcard `"*": ["./*"]`
- Use `import type` / `import { type Foo }` — enables proper tree-shaking
- Relative imports only within same directory (`./sibling`)
- Avoid barrel exports (`export *`) — breaks tree-shaking, hides dependency graph
- Use `verbatimModuleSyntax: true` to enforce explicit type imports

## Common Mistakes

| Pattern | Problem | Fix |
|---------|---------|-----|
| `obj!.prop` | Hides null bugs | Guard or throw with context |
| `as SomeType` | Bypasses type checker | Narrow with `in`, `instanceof`, or discriminant |
| `enum Foo {}` | Numeric enums leak, tree-shake poorly | `as const` object or union type |
| `any` anywhere | Disables type checking entirely | `unknown` + narrowing |
| `Promise<void>` fire-and-forget | Swallows errors silently | `await` or `.catch()` |
| Index signature `[k: string]: T` | Allows any key | `Record<KnownKeys, T>` or `Map` |
| `JSON.parse()` unvalidated | Returns `any`, no runtime safety | Validate with schema (Zod, Valibot, ArkType) |
| `delete obj.key` | Leaves `undefined`, breaks `exactOptionalPropertyTypes` | Destructure or create new object |
| Mutable default params | Shared reference mutation | `readonly` or spread copy |
| `Cannot find name 'process'` → blind `@types/node` install | File may be outside tsconfig `include`, or TS6 omitted `types: ["node"]` | Run **Node types probe** below before installing or rewriting imports |
| IDE says `npm i @types/node` on a pnpm/yarn repo | Wrong package manager; dep may already exist | Honor lockfile; verify `package.json` first |

## Node types probe (implement / fix)

Before adding `@types/node` or rewriting `process` imports, check in order:

1. Is `@types/node` already a devDependency? Is `"types": ["node"]` (or equivalent) in the active tsconfig?
2. Is the failing file listed under that project’s `include` (or covered by a glob)? Framework-generated includes often omit root tooling configs.
3. Only then: add `@types/node` + `types: ["node"]`, **or** add the file to `include`, **or** use `node:process` / a triple-slash reference.

**Anti-trigger:** Do not treat the IDE’s stock “install `@types/node` via npm” tip as the diagnosis when step 1 already passes.

## Logging / Diagnostics

| Prefer | Avoid |
|--------|-------|
| Structured logger (`pino`, `winston`, or project logger) with fields | `console.log` / string concat as the only app logging |
| Redact secrets, tokens, PII from log args | Bearer tokens, passwords, raw PII in messages |
| Low-cardinality metric labels when the stack already uses Prometheus/OTEL | Unbounded ids (`userId`, `orderId`) as label keys |

Cross-language Prefer/Avoid, disposition, **CP027**–**CP029**: [`observability.md`](observability.md).

## Type Utilities Cheat Sheet

```typescript
Partial<T>           // All props optional
Required<T>          // All props required
Readonly<T>          // All props readonly
Pick<T, K>           // Subset of props
Omit<T, K>           // Exclude props
Record<K, V>         // Object with key type K, value type V
Extract<T, U>        // Members of T assignable to U
Exclude<T, U>        // Members of T not assignable to U
NonNullable<T>       // Remove null | undefined
ReturnType<F>        // Return type of function
Awaited<T>           // Unwrap Promise
NoInfer<T>           // Prevent inference from this position (5.4+)
```
