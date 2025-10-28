# Security Protocols

**Authority Level**: DOMAIN-CONDITIONAL (applies to software-development domain)
**Enforcement**: Agents, skills, security-scan skill, code review
**Prerequisite**: Constitutional principles + TDD + Code Quality

---

## Security Statement

**MANDATE**: All code must be secure by design. Security is not an afterthought.

**Security vulnerabilities are constitutional violations.**

---

## OWASP Top 10 (2021)

These are the most critical web application security risks. ALL must be addressed.

### 1. Broken Access Control

**Risk**: Users can access resources they shouldn't.

**Examples**:
- Direct object reference: `/api/users/123` (can access any user)
- Missing authorization checks
- Insecure direct file access

**Prevention**:
```python
# ❌ VULNERABLE - No authorization check
@app.route('/api/orders/<order_id>')
def get_order(order_id):
    order = Order.query.get(order_id)
    return jsonify(order)  # ❌ Anyone can access any order

# ✅ SECURE - Authorization check
@app.route('/api/orders/<order_id>')
@login_required
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        abort(404)
    if order.user_id != current_user.id:  # ✅ Check ownership
        abort(403)
    return jsonify(order)
```

**Checklist**:
- [ ] Every endpoint has authentication check
- [ ] Every resource has authorization check (ownership)
- [ ] Default deny (whitelist, not blacklist)
- [ ] No direct object references without validation

---

### 2. Cryptographic Failures

**Risk**: Sensitive data exposed due to weak/missing encryption.

**Examples**:
- Passwords stored in plaintext
- Weak hashing algorithms (MD5, SHA1)
- Unencrypted data transmission

**Prevention**:
```python
# ❌ VULNERABLE - Plaintext password
class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password  # ❌ Stored plaintext

# ❌ VULNERABLE - Weak hashing
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()  # ❌ MD5 is broken

# ✅ SECURE - bcrypt hashing
import bcrypt

class User:
    def __init__(self, email, password):
        self.email = email
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt(rounds=12)  # ✅ Strong hashing
        )

    def verify_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash
        )
```

**Checklist**:
- [ ] Passwords hashed with bcrypt/argon2 (not MD5/SHA1)
- [ ] Sensitive data encrypted at rest
- [ ] HTTPS for all data in transit
- [ ] No hardcoded secrets in code
- [ ] Secrets in environment variables or secret managers

---

### 3. Injection

**Risk**: Attacker can inject malicious code (SQL, command, LDAP, etc.).

**SQL Injection**:
```python
# ❌ VULNERABLE - SQL injection
user_input = request.args.get('username')
query = f"SELECT * FROM users WHERE username = '{user_input}'"
db.execute(query)  # ❌ Attacker can inject: ' OR '1'='1

# ✅ SECURE - Parameterized query
user_input = request.args.get('username')
query = "SELECT * FROM users WHERE username = ?"
db.execute(query, (user_input,))  # ✅ Safe parameterization
```

**Command Injection**:
```python
# ❌ VULNERABLE - Command injection
filename = request.args.get('file')
os.system(f"cat {filename}")  # ❌ Attacker can inject: "; rm -rf /"

# ✅ SECURE - Avoid shell commands, use libraries
filename = request.args.get('file')
# Validate filename first
if not re.match(r'^[a-zA-Z0-9_.-]+$', filename):
    abort(400)
# Use safe file reading
with open(os.path.join(SAFE_DIR, filename), 'r') as f:
    content = f.read()  # ✅ No shell execution
```

**Checklist**:
- [ ] Parameterized queries (no string concatenation)
- [ ] Input validation (whitelist, not blacklist)
- [ ] Avoid system commands (use libraries)
- [ ] Escape user input in templates

---

### 4. Insecure Design

**Risk**: Fundamental flaws in design, not implementation bugs.

**Examples**:
- No rate limiting → Brute force attacks
- Unlimited file uploads → Denial of service
- No password requirements → Weak passwords

**Prevention**:
```python
# ❌ VULNERABLE - No rate limiting
@app.route('/api/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    # ❌ Attacker can brute force passwords

# ✅ SECURE - Rate limiting
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")  # ✅ Max 5 attempts per minute
def login():
    username = request.json['username']
    password = request.json['password']
    # Rate limited, brute force much harder
```

**Checklist**:
- [ ] Rate limiting on sensitive endpoints
- [ ] File upload size limits
- [ ] Password complexity requirements
- [ ] Multi-factor authentication for sensitive actions
- [ ] Account lockout after failed attempts

---

### 5. Security Misconfiguration

**Risk**: Default configs, unnecessary features, verbose errors.

**Examples**:
- Debug mode in production
- Default credentials
- Unnecessary services enabled
- Stack traces exposed to users

**Prevention**:
```python
# ❌ VULNERABLE - Debug mode in production
app = Flask(__name__)
app.debug = True  # ❌ Exposes stack traces, internal info

# ✅ SECURE - Production configuration
app = Flask(__name__)
app.debug = False  # ✅ Debug off
app.config['ENV'] = 'production'

# Error handling without stack traces
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")  # ✅ Log internally
    return jsonify({"error": "Internal server error"}), 500  # ✅ Generic message
```

**Checklist**:
- [ ] Debug mode off in production
- [ ] No default credentials
- [ ] Unnecessary features disabled
- [ ] Generic error messages (no stack traces to users)
- [ ] Security headers configured

---

### 6. Vulnerable and Outdated Components

**Risk**: Using libraries with known vulnerabilities.

**Prevention**:
```bash
# Check for vulnerabilities
pip-audit  # Python
npm audit  # JavaScript

# Update dependencies regularly
pip install --upgrade <package>
npm update
```

**Checklist**:
- [ ] Dependencies scanned for vulnerabilities
- [ ] Regular dependency updates
- [ ] Automated security alerts (GitHub Dependabot)
- [ ] Pin dependency versions (requirements.txt, package-lock.json)

---

### 7. Identification and Authentication Failures

**Risk**: Weak authentication, session management issues.

**Examples**:
- Weak passwords allowed
- Session fixation
- Session IDs in URL
- No session timeout

**Prevention**:
```python
# ❌ VULNERABLE - Weak password
def create_user(password):
    if len(password) < 6:  # ❌ Too weak
        raise ValueError("Password too short")

# ✅ SECURE - Strong password requirements
def create_user(password):
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters")
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain uppercase letter")
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain lowercase letter")
    if not re.search(r'[0-9]', password):
        raise ValueError("Password must contain number")
    if not re.search(r'[!@#$%^&*]', password):
        raise ValueError("Password must contain special character")
```

**Checklist**:
- [ ] Strong password requirements (length, complexity)
- [ ] Secure session management (HTTP-only cookies)
- [ ] Session timeout
- [ ] Multi-factor authentication
- [ ] Account lockout after failed attempts

---

### 8. Software and Data Integrity Failures

**Risk**: Code/data modified without verification.

**Examples**:
- No code signing
- Insecure CI/CD pipeline
- Auto-update without verification
- Deserialization of untrusted data

**Prevention**:
```python
# ❌ VULNERABLE - Pickle deserialization
import pickle
user_data = pickle.loads(request.data)  # ❌ Arbitrary code execution

# ✅ SECURE - JSON deserialization
import json
user_data = json.loads(request.data)  # ✅ Safe, no code execution
```

**Checklist**:
- [ ] Code signing for releases
- [ ] Secure CI/CD pipeline
- [ ] Integrity checks for dependencies
- [ ] Avoid pickle/yaml.load (use json)

---

### 9. Security Logging and Monitoring Failures

**Risk**: Attacks go undetected due to insufficient logging.

**Prevention**:
```python
import logging

# ✅ SECURE - Log security events
logger = logging.getLogger(__name__)

@app.route('/api/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    user = User.query.filter_by(username=username).first()

    if not user or not user.verify_password(password):
        logger.warning(
            f"Failed login attempt for user: {username} "
            f"from IP: {request.remote_addr}"
        )  # ✅ Log failed attempts
        return jsonify({"error": "Invalid credentials"}), 401

    logger.info(
        f"Successful login for user: {username} "
        f"from IP: {request.remote_addr}"
    )  # ✅ Log successful logins
    return jsonify({"token": generate_token(user)})
```

**Log These Events**:
- Login attempts (success and failure)
- Authorization failures
- Input validation failures
- System errors
- High-value transactions

**Checklist**:
- [ ] Security events logged
- [ ] Logs include timestamp, user, IP, action
- [ ] Logs protected from tampering
- [ ] Log monitoring/alerting configured
- [ ] No sensitive data in logs (passwords, tokens)

---

### 10. Server-Side Request Forgery (SSRF)

**Risk**: Attacker can make server request internal resources.

**Prevention**:
```python
# ❌ VULNERABLE - SSRF
url = request.args.get('url')
response = requests.get(url)  # ❌ Attacker can access internal services

# ✅ SECURE - URL validation
ALLOWED_DOMAINS = ['example.com', 'api.example.com']

def fetch_url(url):
    parsed = urlparse(url)

    # Validate domain
    if parsed.netloc not in ALLOWED_DOMAINS:
        raise ValueError("Domain not allowed")

    # Prevent internal network access
    if parsed.netloc in ['localhost', '127.0.0.1', '0.0.0.0']:
        raise ValueError("Cannot access localhost")

    # Prevent private IP ranges
    ip = socket.gethostbyname(parsed.netloc)
    if ipaddress.ip_address(ip).is_private:
        raise ValueError("Cannot access private IP")

    return requests.get(url, timeout=5)  # ✅ Validated
```

**Checklist**:
- [ ] URL validation (whitelist domains)
- [ ] Block internal network access
- [ ] Block private IP ranges
- [ ] Network segmentation

---

## Security Best Practices

### Input Validation

**Whitelist, not blacklist**:
```python
# ❌ BAD - Blacklist
def validate_username(username):
    if '<' in username or '>' in username:  # ❌ Can miss attacks
        raise ValueError("Invalid characters")

# ✅ GOOD - Whitelist
def validate_username(username):
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):  # ✅ Only allowed chars
        raise ValueError("Invalid characters")
```

### Output Encoding

**Prevent XSS**:
```python
# ❌ VULNERABLE - XSS
from flask import Markup
user_input = request.args.get('name')
return Markup(f"<h1>Hello {user_input}</h1>")  # ❌ XSS possible

# ✅ SECURE - Auto-escaping
from flask import render_template_string
user_input = request.args.get('name')
return render_template_string("<h1>Hello {{ name }}</h1>", name=user_input)  # ✅ Auto-escaped
```

### Secrets Management

**Never hardcode secrets**:
```python
# ❌ VULNERABLE - Hardcoded secret
API_KEY = "sk_live_abc123def456"  # ❌ Committed to git

# ✅ SECURE - Environment variable
import os
API_KEY = os.getenv('API_KEY')  # ✅ From environment
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")
```

**Use secret managers**:
```python
# ✅ BEST - Secret manager
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://myvault.vault.azure.net/", credential=credential)
API_KEY = client.get_secret("api-key").value
```

### Security Headers

**Configure security headers**:
```python
from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app, content_security_policy={
    'default-src': "'self'",
    'script-src': "'self'",
    'style-src': "'self'"
})

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

---

## Security Checklist

Before committing code:

**OWASP Top 10**:
- [ ] Access control on all endpoints
- [ ] Passwords hashed with bcrypt/argon2
- [ ] No SQL/command injection
- [ ] Rate limiting on sensitive endpoints
- [ ] Debug mode off in production
- [ ] Dependencies scanned for vulnerabilities
- [ ] Strong password requirements
- [ ] No pickle/unsafe deserialization
- [ ] Security events logged
- [ ] URL validation, no SSRF

**Best Practices**:
- [ ] Input validation (whitelist)
- [ ] Output encoding (XSS prevention)
- [ ] No hardcoded secrets
- [ ] Security headers configured
- [ ] HTTPS enforced
- [ ] CORS configured properly

**If ANY box is unchecked, code has security vulnerabilities.**

---

## Security Testing

### Static Analysis

```bash
# Python security linting
bandit -r .

# Dependency vulnerability scanning
pip-audit
```

### Dynamic Testing

```bash
# SQL injection testing
sqlmap -u "http://localhost/api/users?id=1"

# XSS testing
# Test with payload: <script>alert('XSS')</script>

# OWASP ZAP for automated scanning
zap-cli quick-scan http://localhost
```

---

## Constitutional Integration

Security protocols enforce constitutional principles:

- **Evidence-Based**: Security tests prove vulnerabilities absent
- **Thoroughness**: All OWASP Top 10 addressed, not just some
- **Transparency**: Security decisions documented and logged
- **No Ambiguity**: Clear security requirements, explicit checks

**Security is not optional. It is constitutional law for software development.**
