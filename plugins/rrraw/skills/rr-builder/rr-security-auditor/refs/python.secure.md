# Python 3.12 Security

Python-specific secure implementation patterns. OWASP principles in `secure.owasp.md`.

---

## Version

Python 3.12+.

---

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| Parameterized queries (sqlite3 `?`, psycopg `%s`) | f-strings in SQL |
| `pathlib` for file operations | `os.path` with string concat |
| `subprocess.run(args_list)` | `os.system()` / `shell=True` |
| Pydantic v2 for input validation | Manual dict access |
| `secrets` module for tokens | `random` |
| `hashlib.scrypt` / `bcrypt` for passwords | MD5/SHA1 |
| `httpx` with timeout | `requests` without timeout |

---

## Common Mistakes

### f-string SQL injection
```python
# BUG
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# FIX
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
# or psycopg: cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### os.system() command injection
```python
# BUG
os.system(f"rm -rf {user_provided_path}")

# FIX
subprocess.run(["rm", "-rf", path], check=True)
# or pathlib: (Path(base) / path).resolve().unlink(missing_ok=True)
```

### pickle.loads() on untrusted data (arbitrary code execution)
```python
# BUG
data = pickle.loads(request.body)

# FIX
import json

data = json.loads(request.body)
# or Pydantic for structured validation
```

### yaml.load() without Loader=SafeLoader
```python
# BUG
config = yaml.load(user_input)

# FIX
config = yaml.safe_load(user_input)
```

### Missing timeout on HTTP requests (SSRF amplification)
```python
# BUG
resp = requests.get(user_provided_url)

# FIX
resp = httpx.get(user_provided_url, timeout=httpx.Timeout(connect=5.0, read=30.0))
```

---

## Django / Framework Patterns

### Server-Controlled Values (Do Not Flag)

Django settings are **deployment configuration**, not attacker input:

```python
# SAFE: All django.conf.settings values are server-controlled
from django.conf import settings

requests.get(settings.EXTERNAL_API_URL)  # NOT SSRF - configured at deployment
requests.get(f"{settings.SEER_URL}{path}")  # NOT SSRF - base URL is server-controlled
open(settings.LOG_FILE_PATH)  # NOT path traversal
db.connect(settings.DATABASE_URL)  # NOT injection

# SAFE: Environment-based configuration
API_URL = os.environ.get("API_URL")
requests.get(API_URL)  # Server operator controls this
```

**Only flag settings-based code if:** The setting value is hardcoded in committed code (secrets) or derived from user input (rare).

### Auto-Escaped (Do Not Flag)

```python
# SAFE: Django auto-escapes template variables
{{variable}}
{{user.name}}
{{form.field}}

# SAFE: ORM methods are parameterized
User.objects.filter(username=user_input)
User.objects.get(id=user_id)
User.objects.exclude(status=status)
MyModel.objects.create(name=name)
```

### Flag These (Django-Specific)

```python
# XSS - Explicit unsafe marking
{{ variable|safe }}                    # FLAG: Disables escaping
{% autoescape off %}...{% endautoescape %}  # FLAG: Disables escaping
mark_safe(user_input)                  # FLAG: If user_input is user-controlled

# SQL Injection
User.objects.raw(f"SELECT * FROM users WHERE name = '{user_input}'")  # FLAG
User.objects.extra(where=[f"name = '{user_input}'"])  # FLAG (deprecated)
RawSQL(f"SELECT * FROM x WHERE y = '{input}'")  # FLAG

# Command Injection
os.system(f"cmd {user_input}")  # FLAG
subprocess.run(cmd, shell=True)  # FLAG if cmd contains user input

# Deserialization - FLAG: pickle on user data, yaml.load without safe_load
```

---

## Search Patterns

```bash
rg "execute\s*\(\s*f['\"]" --type py
```
SQL injection via f-string in execute.

```bash
rg "os\.(system|popen)" --type py
```
Command injection — use subprocess with list args.

```bash
rg "pickle\.loads?" --type py
```
Deserialization risk — use JSON or Pydantic.

```bash
rg "yaml\.load\(" --type py
```
Unsafe YAML — require `Loader=SafeLoader` or use `yaml.safe_load`.

```bash
rg "shell\s*=\s*True" --type py
```
Shell injection — pass args as list, never shell=True.

```bash
rg "random\.(random|randint|choice)" --type py
```
Weak randomness for security — use `secrets` module.

---

## Cross-References

- `secure.owasp.md` — OWASP Top 10 patterns
- `secure.principles.md` — security rules
- `python.md` — Python standards (uv, SQLAlchemy 2.0, Ruff)
