# OWASP Security Patterns (Language-Agnostic)

Detection principles, checklists, and search patterns for OWASP Top 10. Language-specific secure implementation examples live in `{language}.secure.md` files.

---

## 1. Injection (A03:2021)

### SQL Injection

**Principle**: Always use parameterized queries. Never concatenate user input into SQL strings.

**Detection heuristics**:
- String concatenation or interpolation inside query strings
- Dynamic query building without bind parameters
- ORM raw query methods with user input

**Search patterns**:
- `rg "execute\s*\(\s*f['\"]" --type py` — Python f-string in execute
- `rg "prepare\s*\(\s*\`" --type js` — JS template literal in prepare
- `rg "executeQuery\s*\([^?]*\+[^)]*\)" --type java` — Java string concat in executeQuery
- `rg "@Query.*\+\s*" --type java` — Spring @Query with concatenation
- `rg "rawQuery|nativeQuery.*concat" --type kotlin`

### Command Injection

**Principle**: Never pass unsanitized user input to shell commands. Use allowlists or language-native filesystem/process APIs.

**Detection heuristics**:
- Shell execution functions called with user-controlled arguments
- Missing allowlist validation before command execution
- String interpolation in command strings

**Search patterns**:
- `rg "(exec|spawn|execSync)\s*\(" --type js`
- `rg "os\.(system|popen)|subprocess\.(call|run|Popen)" --type py`
- `rg "Runtime\.getRuntime\(\)\.exec|ProcessBuilder" --type java`

### XSS (A07:2021)

**Principle**: Always escape user input when rendering HTML. Use framework auto-escaping. Sanitize when raw HTML is required.

**Detection heuristics**:
- Explicit "unsafe" or "raw" HTML rendering directives
- Disabling auto-escaping in templates
- `innerHTML` assignment from user-controlled data

**Search patterns**:
- `rg "dangerouslySetInnerHTML" --type jsx --type tsx`
- `rg "v-html" --type vue`
- `rg "innerHTML\s*=" --type js --type ts`
- `rg "\|\s*safe" --type html` — Jinja2/Django safe filter
- `rg "Jsoup\.clean" --type java` — verify sanitization is present, not absent

---

## 2. Authentication (A07:2021)

### Session Management Checklist

- [ ] Secrets from environment variables, not hardcoded
- [ ] Access tokens expire ≤1 hour
- [ ] Refresh tokens stored server-side
- [ ] Token validation checks issuer/audience
- [ ] Passwords hashed with bcrypt/scrypt/argon2 (never MD5/SHA1)

### Credential Handling

- [ ] Generic error: "Invalid credentials" (not "User not found" / "Wrong password")
- [ ] Rate limiting: ≤5 attempts/15 min on auth endpoints
- [ ] Account lockout or progressive delay after repeated failures

**Search patterns**:
- `rg "(SECRET|PASSWORD|API_KEY|TOKEN)\s*[:=]\s*['\"][^'\"]+['\"]"` — hardcoded secrets (any language)
- `rg "MD5|SHA-1|sha1" --type java --type py --type js` — weak hashing

---

## 3. Access Control (A01:2021)

### IDOR (Insecure Direct Object Reference)

**Principle**: Never expose data based solely on knowing an ID. Always verify ownership/permissions server-side.

**Detection heuristics**:
- Endpoint fetches resource by ID without checking authenticated user's ownership
- Missing authorization middleware/annotation on data-access endpoints
- Path/query parameter used directly in DB lookup without ownership filter

**Search patterns**:
- `rg "app\.(get|post|put|delete)\s*\(" --type js -A 5 | rg -v "auth"` — unprotected Express routes
- `rg "@(Get|Post|Put|Delete)Mapping" --type java -A 5 | rg -v "@PreAuthorize"` — unprotected Spring endpoints
- `rg "@app\.route" --type py -A 5 | rg -v "login_required"` — unprotected Flask routes

### Authorization Checklist

- [ ] Every endpoint checks user permissions before returning data
- [ ] Admin endpoints verify role (not just authentication)
- [ ] Horizontal escalation prevented (user A cannot access user B's data)
- [ ] Vertical escalation prevented (user cannot elevate to admin)
- [ ] Default-deny: new endpoints require explicit permission grants

---

## 4. Security Misconfiguration (A05:2021)

### CORS

**Principle**: Production must explicitly allow only trusted origins. Development can be permissive.

**Detection heuristics**:
- Wildcard `*` origin in production config
- CORS enabled globally without origin restriction
- Credentials allowed with wildcard origin (browser rejects this, but signals misconfiguration)

**Search patterns**:
- `rg "cors\(\)" --type js` — Express default (allows all)
- `rg "Access-Control-Allow-Origin.*\*"` — wildcard in any config
- `rg "allowedOrigins\s*\(\s*\"\*\"\)" --type java` — Spring wildcard

### Security Headers (Production)

- [ ] `X-Frame-Options: DENY` or `SAMEORIGIN`
- [ ] `Strict-Transport-Security` (HSTS) with `max-age ≥ 31536000`
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Powered-By` removed
- [ ] `Content-Security-Policy` configured
- [ ] Security header middleware enabled (helmet, Spring Security headers, Talisman, etc.)

---

## 5. Cryptographic Failures (A02:2021)

- [ ] PII only in database, never in logs/code
- [ ] Passwords never logged
- [ ] API keys in environment variables only
- [ ] HTTPS enforced in production (TLS 1.2 minimum, prefer 1.3)
- [ ] No weak algorithms (MD5, SHA1, DES, RC4)

**Search patterns**:
- `rg "(console|logger|log)\.(log|info|debug|warn).*\b(password|email|ssn|credit.?card)\b"` — PII in logs
- `rg "MD5|DES|RC4|SHA-1" --type java --type py --type js` — weak crypto

---

## 6. Vulnerable Dependencies (A06:2021)

**Principle**: Audit dependencies regularly. Pin versions. Update within 6 months.

**Language-specific audit commands**:
- Java/Kotlin: `mvn dependency-check:check` or `gradle dependencyCheckAnalyze`
- JavaScript: `npm audit --audit-level=high`
- Python: `pip-audit` or `safety check`
- Rust: `cargo audit`

**Checklist**:
- [ ] No critical/high vulnerabilities
- [ ] Lock file committed (package-lock.json, pom.xml, Cargo.lock, etc.)
- [ ] Dependencies updated within 6 months
- [ ] Transitive dependencies reviewed for known CVEs

---

## 7. SSRF (A10:2021)

**Principle**: Never let user input control outbound request URLs without validation. Block internal network access.

**Detection heuristics**:
- HTTP client called with user-provided URL
- Missing URL allowlist or hostname validation
- No blocking of localhost/private IP ranges (127.x, 10.x, 172.16-31.x, 192.168.x)

**Search patterns**:
- `rg "(fetch|axios|http\.get|HttpClient|requests\.get)\s*\(.*req\." --type js --type java --type py`
- `rg "URL\(.*request\." --type java --type kotlin`

---

## 8. Mass Assignment

**Principle**: Never bind user input directly to domain objects without explicit field allowlisting.

**Detection heuristics**:
- Request body mapped directly to entity/model without DTO
- ORM `update` with raw request body
- Missing `@JsonIgnore` or equivalent on sensitive fields (role, isAdmin, permissions)

**Search patterns**:
- `rg "req\.body\.(role|isAdmin|permissions)" --type js`
- `rg "@RequestBody.*Entity" --type java` — entity used directly as request body
- `rg "\.update\(.*request\.(body|json)" --type py`

---

## 9. Business Logic

**Common vulnerabilities**:
- Race conditions in financial operations (double-spend, double-submit)
- Negative quantities in orders
- Price manipulation via client-submitted values
- Bypassing workflow steps (e.g., skipping payment, jumping status)
- Time-of-check-to-time-of-use (TOCTOU) bugs

**Search patterns**:
- `rg "req\.(body|query|params)\.(price|amount|total|quantity)" --type js --type ts`
- `rg "@RequestParam.*price|@RequestBody.*amount" --type java`

---

## 10. Logging & Monitoring (A09:2021)

### What to Log
Auth attempts (success + failure), authorization failures, input validation failures, rate limit triggers, sensitive data access, admin operations

### What NOT to Log
Passwords, credit card numbers, PII (emails, names, phone numbers), session tokens, API keys

### Checklist
- [ ] Failed auth attempts logged with IP and timestamp
- [ ] Structured logging format (JSON) for machine parsing
- [ ] Log correlation via trace IDs
- [ ] Alerts configured for anomalous patterns (brute force, privilege escalation attempts)

---

## 11. Resource Exhaustion — Always Have Limits (A04:2021)

**Principle:** Any cache, collection, queue, buffer, retry loop, upload handler, or request-body handling that can grow from traffic or input **must** have a defined runtime max. An ADR that accepts unbounded growth **does not** waive this check — a **runtime** limit must still exist.

**Fail if:** **New/changed** cache, collection, queue, buffer, retry loop, upload, or request-body handling can grow from traffic or input **without** a defined max (size, count, TTL+eviction, or payload limit).

**Pass if:** A bound is explicit in code or config the runtime enforces (max entries, max bytes, max retries, max body).

**Severity:** **High** when input or cardinality is attacker- or traffic-influenced (OWASP A04:2021 / DoS-class).

**Do not flag:**
- Tiny fixed-size locals (stack arrays, small const buffers)
- Framework max already applied — cite the framework default or config
- Test-only fixtures with bounded scope

**Detection heuristics:**
- Unbounded `Map`/`HashMap`/`dict` used as cache with no eviction or max size
- Retry loops with no max attempts or unbounded backoff accumulation
- In-memory queues/lists that append without cap or TTL
- File/body upload handlers without `maxSize` / `limit` / `Content-Length` enforcement
- User-influenced collections grown in a loop without admission control

**Search patterns:**
- `rg "new (HashMap|ConcurrentHashMap|Map|dict)\(\)"` in cache-like contexts without `maxSize|maximumSize|evict|expire|limit`
- `rg "while\s*\(.*retry|for\s*\(.*retry"` without `maxRetries|MAX_RETRIES|attempts\s*<`
- `rg "upload|multipart|bodyParser|maxBody|maxRequest"` — verify limits on new/changed handlers
- `rg "unbounded|no limit|grow forever"` in comments or config (investigate, do not auto-flag)

**Compensating control:** Explicit max in code/config that the runtime enforces can Pass. Document the bound in the finding's fix column when recommending.

---

## Cross-References

- **Principles & rules**: `secure.principles.md`
- **Java/Kotlin security**: `java.secure.md`, `kotlin.secure.md`
- **TypeScript/React security**: `typescript.secure.md`, `react.secure.md`
- **Python security**: `python.secure.md`
- **Spring Security specifics**: [`skills/code/coder/refs/java.spring.md`](../../code/coder/refs/java.spring.md) § Security
