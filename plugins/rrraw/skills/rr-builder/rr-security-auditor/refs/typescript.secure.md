# TypeScript 5.7 Security (Language-Level)

TypeScript-specific secure patterns. React patterns in `react.secure.md`. OWASP in `secure.owasp.md`.

---

## Version

TypeScript 5.7+ with `strict: true`, `strictNullChecks: true`.

---

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| Branded types for sensitive values (`UserId`, `Email`) | Raw `string` for IDs/emails |
| `unknown` for external data + runtime validation (Zod) | `any` or type assertions |
| Strict null checks (`strictNullChecks: true`) | Loose config |
| Discriminated unions for error handling | Thrown strings |
| `as const` for permission enums | Mutable string arrays |
| Template literal types for URL patterns | Raw string |

---

## Common Mistakes

### Type assertion on API response without runtime validation
```typescript
// BUG
const user = await fetch('/api/user').then(r => r.json()) as User;

// FIX
const schema = z.object({ id: z.string(), email: z.string().email() });
const user = schema.parse(await fetch('/api/user').then(r => r.json()));
```

### `any` hiding injection vectors
```typescript
// BUG
function runQuery(sql: any) { db.execute(sql); }

// FIX
function runQuery(sql: string, params: readonly unknown[]) { db.execute(sql, params); }
```

### Non-exhaustive switch on permission enum (missing case = unauthorized access)
```typescript
// BUG
type Permission = 'read' | 'write' | 'admin';
function canAccess(p: Permission) {
  switch (p) { case 'read': return true; case 'write': return true; }
}

// FIX
function assertNever(x: never): never { throw new Error(`Unhandled: ${x}`); }
function canAccess(p: Permission) {
  switch (p) {
    case 'read': return true;
    case 'write': return true;
    case 'admin': return true;
    default: return assertNever(p);
  }
}
```

### Prototype pollution via Object.assign with user input
```typescript
// BUG
const config = Object.assign({}, defaultConfig, req.body);

// FIX
const safe = Object.fromEntries(
  Object.entries(req.body).filter(([k]) => !k.startsWith('__') && k !== 'constructor' && k !== 'prototype')
);
const config = { ...defaultConfig, ...safe };
```

---

## Framework Mitigations (React / Vue)

### Auto-Escaped (Do Not Flag)

```jsx
// SAFE: JSX auto-escapes interpolated values
<div>{userInput}</div>
<span>{user.name}</span>
<p>{data.description}</p>
<div className={userInput} />
<input value={userInput} />
```

```vue
<!-- SAFE: Vue auto-escapes interpolation -->
<div>{{ userInput }}</div>
<span>{{ user.name }}</span>
<div :class="userInput" />
<input :value="userInput" />
```

### Flag These (React/Vue)

- Raw HTML injection with user input (React pattern)
- `v-html="userInput"` (Vue)
- `href={userInput}` or `:href="userInput"` without protocol validation (javascript: XSS)
- Dynamic code execution with user input

---

## Search Patterns

```bash
rg "\bas\b\s+\w+" --type ts
```
Type assertions — verify runtime validation exists.

```bash
rg ": any\b" --type ts
```
`any` types — replace with `unknown` + narrowing.

```bash
rg "Object\.assign\(.*req\." --type ts
```
Prototype pollution risk — use allowlisted spread.

```bash
rg "eval\(|Function\(" --type ts
```
Code execution — never use on user input.

---

## Cross-References

- `secure.owasp.md` — OWASP Top 10 patterns
- `secure.principles.md` — security rules
- `typescript.md` — TypeScript standards
- `react.secure.md` — React-specific security
