# React 18 Security (Frontend)

React/frontend-specific secure implementation patterns. OWASP principles live in `secure.owasp.md`.

## Auto-Escaped (Do Not Flag)

```tsx
// SAFE: JSX auto-escapes interpolated values
<div>{userInput}</div>
<span>{user.name}</span>
<p>{data.description}</p>
<div className={userInput} />
<input value={userInput} />
```

## Version
React 18.x, TypeScript 5.7+.

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| `{variable}` auto-escaping | `dangerouslySetInnerHTML` with user content |
| DOMPurify when raw HTML required | Unsanitized HTML injection |
| `httpOnly` + `secure` + `sameSite` cookies for tokens | localStorage for auth tokens |
| Server-side token validation | Client-only auth checks |
| Build-time env injection (public config only) | Secrets in `REACT_APP_` / `VITE_` (bundled, public) |
| CSP headers, nonce-based scripts | Inline scripts, `eval()` |
| URL validation before navigation | `window.location = userInput` |
| Typed API responses (Zod/io-ts) | Trusting API response shape |

## Common Mistakes

### dangerouslySetInnerHTML with unsanitized user content (XSS)
```tsx
// BUG
<div dangerouslySetInnerHTML={{ __html: userComment }} />

// FIX
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userComment) }} />
```

### Storing JWT in localStorage (accessible to XSS)
```tsx
// BUG: any XSS can steal token
localStorage.setItem('token', jwt);

// FIX: httpOnly cookie (Set-Cookie: HttpOnly; Secure; SameSite=Strict)
fetch('/api/login', { credentials: 'include' });
```

### Client-side only route protection
```tsx
// BUG: server returns data anyway; client guard is cosmetic
if (!user) return <Navigate to="/login" />;
// FIX: server validates token on every request; client guard is UX only
```

### Leaking secrets via env vars (bundled, public)
```tsx
// BUG: REACT_APP_* and VITE_* are embedded in client bundle
const apiKey = process.env.REACT_APP_SECRET_KEY;

// FIX: only non-secret config (API base URL, feature flags); secrets stay server-side
const apiBase = import.meta.env.VITE_API_BASE_URL;
```

### href={userInput} without protocol validation (javascript: XSS)
```tsx
// BUG
<a href={userProvidedUrl}>Link</a>

// FIX
const safeUrl = userProvidedUrl.startsWith('https://') || userProvidedUrl.startsWith('http://')
  ? userProvidedUrl : '#';
<a href={safeUrl} rel="noopener noreferrer">Link</a>
```

### Unsafe img/iframe src from user input
```tsx
// BUG: data: or javascript: URLs can execute
<img src={userAvatarUrl} />

// FIX: allowlist protocol and origin, or proxy through backend
const allowed = /^https:\/\/(cdn\.example\.com|trusted\.com)\//.test(userAvatarUrl);
<img src={allowed ? userAvatarUrl : '/placeholder.svg'} />
```

## Search Patterns

```bash
rg "dangerouslySetInnerHTML" --type tsx --type jsx
```
Verify DOMPurify or equivalent.

```bash
rg "localStorage\.(set|get)Item.*token" --type ts --type tsx
```
Prefer httpOnly cookies.

```bash
rg "window\.location\s*=" --type ts --type tsx
```
Check for user input.

```bash
rg "href=\{[^}]*\}" --type tsx
```
Verify protocol validation.

```bash
rg "REACT_APP_SECRET|VITE_SECRET|VITE_API_KEY" --type ts
```
Never bundle secrets.

```bash
rg "src=\{[^}]*\}" --type tsx -A 0
```
Verify URL allowlist.

## Cross-References

- `secure.owasp.md` | `secure.principles.md` | `react-18.md` | `typescript.secure.md`
