---
name: security-scan
category: software
domain: software-development
version: 1.0.0
authority: domain-specific
description: Security scan OWASP Top 10 vulnerability check security audit XSS SQL injection CSRF authentication security authorization vulnerabilities security testing penetration testing security assessment automated security scan vulnerability detection security validation secure code review security best practices check for security flaws security compliance OWASP compliance security standards enforcement security gates security quality security requirements validation security testing framework security analysis security inspection vulnerability scanning security verification secure coding practices input validation security authentication bypass security SQL injection detection XSS prevention CSRF protection insecure deserialization broken authentication sensitive data exposure XXE injection security misconfiguration using components with known vulnerabilities insufficient logging monitoring API security web application security
---

# Security Scan

**Purpose**: Scan code for security vulnerabilities against OWASP Top 10. Detect common security flaws before deployment.

**Domain**: Software Development

**Authority**: Domain-specific security enforcement

---

## 📋 When to Invoke

**Invoke this skill when**:
- After implementing security-sensitive features (senior-developer)
- During security testing (test-engineer)
- Before deployment (test-engineer)
- After refactoring authentication/authorization code (pruner)
- During security audit (any agent)

**Keywords that trigger this skill**:
- "security scan"
- "OWASP check"
- "vulnerability scan"
- "security audit"
- "check for vulnerabilities"
- "security testing"
- "XSS check"
- "SQL injection"

---

## 🎯 OWASP Top 10 (From Methodology)

This skill enforces standards from `@.claude/methodologies/software/security-protocols.md`:

### OWASP Top 10 (2021)

1. **Broken Access Control**
2. **Cryptographic Failures**
3. **Injection** (SQL, NoSQL, Command)
4. **Insecure Design**
5. **Security Misconfiguration**
6. **Vulnerable and Outdated Components**
7. **Identification and Authentication Failures**
8. **Software and Data Integrity Failures**
9. **Security Logging and Monitoring Failures**
10. **Server-Side Request Forgery (SSRF)**

---

## 📋 Skill Procedure

### Step 1: Determine Scan Scope

```yaml
scan_scope:
  files: [{{FILE_LIST}}]
  modules: [{{MODULE_LIST}}]
  focus_areas:
    - "{{authentication}}"
    - "{{api_endpoints}}"
    - "{{database_queries}}"
    - "{{user_input_handling}}"
    - "{{file_operations}}"
```

---

### Step 2: Automated Security Scanning

#### Tool Selection by Language

```yaml
security_tools:
  python: "bandit, safety, pip-audit"
  javascript: "npm audit, eslint-plugin-security"
  typescript: "npm audit, tslint-config-security"
  go: "gosec"
  rust: "cargo-audit"
```

**For Python projects**:

```bash
# 1. Bandit - Security linter
bandit -r src/ -f json -o bandit-report.json

# 2. Safety - Check dependencies for known vulnerabilities
safety check --json

# 3. Pip-audit - Audit Python packages
pip-audit --format=json
```

---

### Step 3: OWASP Top 10 Checks

#### 1. Broken Access Control

**Check for**:
- Missing authorization checks
- Direct object reference without validation
- Elevation of privilege vulnerabilities

**Manual review**:
```yaml
access_control_check:
  - endpoint: "{{API_ENDPOINT}}"
    authorization: "{{PRESENT|MISSING}}"
    location: "{{FILE}}:{{LINE}}"
    vulnerability: "{{YES|NO}}"
    severity: "{{CRITICAL|HIGH|MEDIUM|LOW}}"
```

**Example patterns to flag**:
```python
# ❌ BAD: No authorization check
@app.route('/admin/delete-user/<user_id>')
def delete_user(user_id):
    User.query.filter_by(id=user_id).delete()

# ✅ GOOD: Authorization check
@app.route('/admin/delete-user/<user_id>')
@require_admin
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
    User.query.filter_by(id=user_id).delete()
```

---

#### 2. Cryptographic Failures

**Check for**:
- Hardcoded secrets/passwords
- Weak hashing algorithms (MD5, SHA1)
- Unencrypted sensitive data

**Automated scan (Bandit)**:
```bash
bandit -r src/ -f json | jq '.results[] | select(.issue_text | contains("hardcoded"))'
```

**Patterns to flag**:
```python
# ❌ BAD: Hardcoded secret
API_KEY = "sk_live_abc123def456"

# ❌ BAD: Weak hashing
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()

# ✅ GOOD: Environment variable + strong hashing
API_KEY = os.getenv('API_KEY')
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

---

#### 3. Injection (SQL, Command, etc.)

**Check for**:
- SQL injection (string concatenation in queries)
- Command injection (unsanitized input to shell)
- NoSQL injection

**Automated scan**:
```bash
# Bandit checks for SQL injection patterns
bandit -r src/ -s B608  # SQL injection
```

**Patterns to flag**:
```python
# ❌ BAD: SQL injection vulnerable
query = f"SELECT * FROM users WHERE username = '{username}'"
db.execute(query)

# ❌ BAD: Command injection vulnerable
os.system(f"ping {user_input}")

# ✅ GOOD: Parameterized query
query = "SELECT * FROM users WHERE username = ?"
db.execute(query, (username,))

# ✅ GOOD: Input validation + safe execution
if re.match(r'^[a-zA-Z0-9.-]+$', hostname):
    subprocess.run(['ping', '-c', '1', hostname])
```

---

#### 4. Insecure Design

**Check for**:
- Missing rate limiting
- No input validation
- Weak password requirements
- Missing CSRF protection

**Manual review checklist**:
```yaml
design_security:
  - feature: "{{FEATURE_NAME}}"
    rate_limiting: "{{PRESENT|MISSING}}"
    input_validation: "{{PRESENT|MISSING}}"
    csrf_protection: "{{PRESENT|MISSING}}"
    password_policy: "{{STRONG|WEAK|NONE}}"
```

---

#### 5. Security Misconfiguration

**Check for**:
- Debug mode enabled in production
- Default credentials
- Verbose error messages exposing internals
- Missing security headers

**Patterns to flag**:
```python
# ❌ BAD: Debug mode in production
app = Flask(__name__)
app.debug = True

# ❌ BAD: Exposing internal errors
@app.errorhandler(500)
def handle_error(e):
    return str(e), 500  # Exposes stack trace

# ✅ GOOD: Generic error message
@app.errorhandler(500)
def handle_error(e):
    logger.error(f"Internal error: {e}")
    return "Internal server error", 500
```

---

#### 6. Vulnerable Components

**Check for**:
- Outdated dependencies with known CVEs

**Automated scan**:
```bash
# Check for vulnerable packages
pip-audit --format=json

# Check for outdated packages
pip list --outdated
```

**Parse results**:
```yaml
vulnerable_components:
  - package: "{{PACKAGE_NAME}}"
    version: "{{CURRENT_VERSION}}"
    vulnerability: "{{CVE_ID}}"
    severity: "{{CRITICAL|HIGH|MEDIUM|LOW}}"
    fixed_in: "{{FIXED_VERSION}}"
```

---

#### 7. Authentication Failures

**Check for**:
- Weak password requirements
- No account lockout
- Session management issues
- Credential stuffing vulnerabilities

**Manual review**:
```yaml
authentication_check:
  - feature: "login"
    password_requirements:
      min_length: {{NUMBER}}
      requires_uppercase: "{{YES|NO}}"
      requires_numbers: "{{YES|NO}}"
      requires_special: "{{YES|NO}}"
    account_lockout: "{{PRESENT|MISSING}}"
    session_timeout: "{{MINUTES}}"
    mfa_support: "{{PRESENT|MISSING}}"
```

---

#### 8. Data Integrity Failures

**Check for**:
- Insecure deserialization
- Missing integrity checks

**Patterns to flag**:
```python
# ❌ BAD: Insecure deserialization
import pickle
data = pickle.loads(user_input)  # Arbitrary code execution risk

# ✅ GOOD: Safe deserialization
import json
data = json.loads(user_input)  # Only deserializes JSON
```

---

#### 9. Logging and Monitoring Failures

**Check for**:
- Missing security event logging
- Logging sensitive data
- No alerting on critical events

**Manual review**:
```yaml
logging_check:
  - event: "{{EVENT_TYPE}}"
    logged: "{{YES|NO}}"
    severity: "{{INFO|WARNING|ERROR|CRITICAL}}"
    includes_sensitive_data: "{{YES|NO}}"
```

---

#### 10. SSRF (Server-Side Request Forgery)

**Check for**:
- Unsanitized URLs in HTTP requests
- Missing allowlist for external requests

**Patterns to flag**:
```python
# ❌ BAD: SSRF vulnerable
url = request.args.get('url')
response = requests.get(url)  # Could request internal services

# ✅ GOOD: URL allowlist
ALLOWED_DOMAINS = ['api.example.com', 'trusted.com']
parsed = urlparse(url)
if parsed.netloc in ALLOWED_DOMAINS:
    response = requests.get(url)
```

---

### Step 4: Aggregate Results

```yaml
security_scan_results:
  timestamp: "{{ISO_8601}}"
  files_scanned: {{COUNT}}

  automated_findings:
    tool: "{{TOOL_NAME}}"
    total_issues: {{COUNT}}
    by_severity:
      critical: {{COUNT}}
      high: {{COUNT}}
      medium: {{COUNT}}
      low: {{COUNT}}

  manual_findings:
    total_issues: {{COUNT}}
    by_severity:
      critical: {{COUNT}}
      high: {{COUNT}}
      medium: {{COUNT}}
      low: {{COUNT}}

  owasp_coverage:
    - category: "Broken Access Control"
      issues_found: {{COUNT}}
      status: "{{PASS|FAIL}}"
    - category: "Cryptographic Failures"
      issues_found: {{COUNT}}
      status: "{{PASS|FAIL}}"
    # ... (all 10 categories)
```

---

### Step 5: Generate Security Report

```markdown
## Security Scan Report

**Project**: {{PROJECT_NAME}}
**Timestamp**: {{TIMESTAMP}}
**Scan Tool**: {{TOOL}}

---

### Executive Summary

**Status**: {{✅ PASS | ⚠️ WARNING | ❌ CRITICAL ISSUES}}

**Total Issues**: {{COUNT}}
- Critical: {{COUNT}}
- High: {{COUNT}}
- Medium: {{COUNT}}
- Low: {{COUNT}}

---

### OWASP Top 10 Assessment

| Category | Issues | Status |
|----------|--------|--------|
| Broken Access Control | {{COUNT}} | {{✅|❌}} |
| Cryptographic Failures | {{COUNT}} | {{✅|❌}} |
| Injection | {{COUNT}} | {{✅|❌}} |
| Insecure Design | {{COUNT}} | {{✅|❌}} |
| Security Misconfiguration | {{COUNT}} | {{✅|❌}} |
| Vulnerable Components | {{COUNT}} | {{✅|❌}} |
| Authentication Failures | {{COUNT}} | {{✅|❌}} |
| Data Integrity Failures | {{COUNT}} | {{✅|❌}} |
| Logging Failures | {{COUNT}} | {{✅|❌}} |
| SSRF | {{COUNT}} | {{✅|❌}} |

---

### Critical Issues (MUST FIX)

{{#if critical_issues}}
{{CRITICAL_ISSUES_LIST}}
{{/if}}

{{#if no_critical}}
✅ No critical security issues found
{{/if}}

---

### High Priority Issues (Should Fix)

{{HIGH_PRIORITY_LIST}}

---

### Recommendations

1. **{{RECOMMENDATION_1}}**
2. **{{RECOMMENDATION_2}}**

---

### Deployment Status

{{#if pass}}
✅ **PASS** - No critical security issues. Safe to deploy.
{{/if}}

{{#if warning}}
⚠️ **WARNING** - Non-critical issues found. Review before deployment.
{{/if}}

{{#if fail}}
❌ **FAIL** - Critical security issues found. DO NOT DEPLOY.

**Required fixes before deployment**:
{{REQUIRED_FIXES}}
{{/if}}
```

---

## 🔗 Integration with Constitutional Principles

This skill enforces:
- ✅ **Evidence-based**: Cites specific file:line for vulnerabilities
- ✅ **Complete transparency**: Explains each vulnerability found
- ✅ **Thoroughness**: Checks all OWASP Top 10 categories

---

## 📊 Output Format

```yaml
security_scan:
  timestamp: "{{ISO_8601}}"
  status: "{{PASS|WARNING|FAIL}}"

  issues:
    critical: {{COUNT}}
    high: {{COUNT}}
    medium: {{COUNT}}
    low: {{COUNT}}

  owasp_top_10:
    - category: "{{CATEGORY}}"
      issues: {{COUNT}}
      status: "{{PASS|FAIL}}"

  safe_for_deployment: "{{YES|NO}}"
```

---

## 💡 Usage Examples

### Example 1: Pre-Deployment Scan

**test-engineer**:
```
Running security scan before deployment...

Using security-scan skill...

Result: ✅ PASS
- 0 critical issues
- 2 medium issues (verbose error messages)
- OWASP Top 10: All categories pass

Safe to deploy with minor improvements recommended.
```

### Example 2: Critical Vulnerability Found

**test-engineer**:
```
Scanning authentication module...

Using security-scan skill...

Result: ❌ CRITICAL ISSUES
- SQL injection in login.py:45 (user input not sanitized)
- Hardcoded API key in config.py:12

DO NOT DEPLOY - Critical vulnerabilities must be fixed.
```

---

## 🎯 Success Criteria

- [ ] Automated security scan completed
- [ ] All OWASP Top 10 categories checked
- [ ] Issues categorized by severity
- [ ] File:line citations provided
- [ ] Deployment status determined (PASS/WARNING/FAIL)

---

**This skill ensures code is secure before deployment.**

**Version**: 1.0.0
**Last Updated**: 2025-10-27
