# Security Rules

## Core Principle
**Security by default** - prevent common vulnerabilities through secure patterns and automated checks.

**Rule IDs:** emit **`CWE-NNN`** (see [secure.owasp.md](secure.owasp.md)). OWASP Top 10 labels are optional secondary context only.

## Auto-Enforced: Secrets & PII Protection

### Secrets Management
- **Never hardcode secrets** (**CWE-798**) - API keys, passwords, tokens go in environment variables only
- **Access pattern**: Use language-appropriate environment variable access (System.getenv, os.Getenv, process.env, etc.)
- **Ensure `.gitignore` excludes** `.env`, `.env.local` files

### Auto-Block: Committing Secrets
**Refuse to commit** files containing:
- Patterns: `password=`, `api_key=`, `secret=`, `token=` with actual values
- AWS keys, private keys, certificates with actual credentials

### PII (Personally Identifiable Information)

**What is PII**: Names, emails, addresses, phone numbers, IDs, financial info, health data

### Auto-Block: Committing PII
**Refuse to commit** files with:
- Real email addresses (except example.com, test.com)
- Phone numbers in realistic formats

### Storage & Logging Rules
- **Database only** - PII goes in database, never in code or logs
- **Git must be PII-free** - no real user data in commits
- **Test data**: Use fake data ("test@example.com", "John Doe")
- **Backups**: Encrypt database backups containing PII
- **Never log PII** (**CWE-532**): emails, names, phone numbers (safe to log: user IDs, timestamps, action types, error codes)

### Always Have Limits (**CWE-770**)

Runtime bounds required for caches, queues, retries, uploads, request bodies. **Full fail/pass criteria and search patterns:** [secure.owasp.md](secure.owasp.md) §11. ADR does not waive.

## .gitignore Enforcement

Always exclude from version control:
- `.env`, `.env.local` (secrets)
- Database files (`.db`, `.sqlite`, etc.) - may contain PII
- Dependency directories (`node_modules/`, `venv/`, `vendor/`)
- Build artifacts (`dist/`, `build/`, `target/`)
- Logs (`*.log`)
- OS files (`.DS_Store`, `Thumbs.db`)
- IDE files (`.vscode/`, `.idea/` - unless shared team settings)

## Environment-Based Security Rules

The following rules apply differently based on environment:

### Development Mode
- Relaxed CORS (allow localhost origins)
- HTTP allowed (no HTTPS requirement)
- Verbose error messages (for debugging)
- Authorization can be stubbed (with clear TODOs)

### Production Mode
- Strict CORS (explicit allowed origins only)
- HTTPS required (enforce via redirect or HSTS)
- Generic error messages (no stack traces)
- Full authorization enforcement
- Security headers enabled (X-Frame-Options, X-Content-Type-Options, etc.)
- Use security header middleware (helmet.js, secure_headers gem, etc.)

### Authorization Rules (**CWE-862** / **CWE-863** / **CWE-639**) - Production Only
- Every endpoint must check user permissions before returning data
- Implement role-based access control (RBAC) - default choice for authorization
- Never expose data based solely on knowing an ID (IDOR prevention — **CWE-639**)
- Log access attempts for audit trail (**CWE-778**)

### HTTPS & Secure Transport (**CWE-319**) - Production Only
- All traffic must use HTTPS (enforce via redirect or HSTS)
- Cookies must have `Secure` and `HttpOnly` flags
- Use `SameSite=Strict` or `SameSite=Lax` for cookies
- TLS 1.2 minimum (prefer TLS 1.3)

### CORS Configuration (**CWE-942**) - Production Only
- Explicit allowed origins (no `*` wildcard)
- Restrict methods to only those needed
- Set `Access-Control-Max-Age` for preflight caching
- Enable credentials only when necessary

### Security Headers (**CWE-693**) - Production Only
- Enable header middleware (helmet, Spring Security headers, etc.)

## Definition of Done - Security

- [ ] No hardcoded secrets (**CWE-798**) (API keys, passwords, tokens in .env only)
- [ ] No PII in code, logs, or commits (**CWE-532**) (use test data)
- [ ] All user input validated
- [ ] .gitignore excludes .env, database files, logs
- [ ] Production: HTTPS enforced (**CWE-319**), security headers set (**CWE-693**)
- [ ] Production: Authorization enforced on all endpoints (**CWE-862** / **CWE-863**)
- [ ] Dependencies up-to-date, no critical vulnerabilities (**CWE-1395**)
- [ ] Security audit passes (no **CWE-89** / **CWE-79** / **CWE-639** / **CWE-918**)
- [ ] Caches, collections, queues, buffers, retries, and uploads have runtime-enforced limits (**CWE-770**)

For CWE detection patterns and checklists, see `secure.owasp.md`.
For language-specific secure implementation examples: `java.secure.md`, `kotlin.secure.md`, `typescript.secure.md`, `react.secure.md`, `python.secure.md`.
For confidence levels, server-controlled vs attacker-controlled, and framework-mitigated patterns, see `confidence.md`.
