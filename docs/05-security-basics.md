# Backend Security Basics

This file covers common security concepts and the minimum practices expected in backend applications.

## JWT

### Definition
JWT stands for JSON Web Token. It is a signed token that carries claims about a user or session.

### Important Practices
- Sign tokens with strong keys.
- Keep access tokens short-lived.
- Validate issuer, audience, expiration, and signature.
- Do not place sensitive secrets in token payloads.

### Why It Matters
JWTs are portable and convenient, but insecure validation leads to account compromise.

## Refresh Tokens

### Definition
Refresh tokens are long-lived credentials used to obtain new short-lived access tokens.

### Important Practices
- Store them more securely than access tokens.
- Rotate them when possible.
- Revoke them on logout, theft suspicion, or password change.

### Why It Matters
They reduce repeated logins while limiting exposure of access tokens.

## Session Cookies and JSESSIONID

### Definition
A session cookie stores an identifier that links the client to server-side session state. In Java applications this is often `JSESSIONID`; in Django the common session cookie is `sessionid`.

### Important Practices
- Mark cookies as `HttpOnly`, `Secure`, and preferably `SameSite`.
- Rotate sessions after login or privilege changes.
- Expire sessions appropriately.

### Why It Matters
Poor session handling enables hijacking and fixation attacks.

## CSRF Tokens

### Definition
A CSRF token is a secret tied to the user session or browser context that helps prove a state-changing request came from a trusted origin.

### Important Practices
- Require CSRF protection for browser-based authenticated writes.
- Combine CSRF tokens with `SameSite` cookies and origin validation.
- Do not disable CSRF checks casually.

### Why It Matters
Without CSRF protection, an attacker can trick a logged-in browser into sending unwanted actions.

## Throttling and Rate Limiting

### Throttling
- **Definition:** Controlling how quickly actions are processed over time.
- **Practice:** Apply tighter limits to expensive or abuse-prone endpoints.
- **Reason:** Protects shared resources and improves fairness.

### Rate Limiting
- **Definition:** Enforcing a maximum number of requests in a defined period.
- **Practice:** Limit by user, token, IP, or endpoint as appropriate.
- **Reason:** Prevents abuse, brute force attempts, and accidental overload.

## Other Basic Security Implementations

### Input Validation
- Validate type, length, format, and allowed values.
- Reason: Rejects malformed or malicious input early.

### Output Encoding
- Encode untrusted data before rendering in HTML or JavaScript.
- Reason: Helps prevent cross-site scripting.

### Least Privilege
- Give users, services, and database accounts only the permissions they need.
- Reason: Limits blast radius during compromise.

### Secrets Management
- Store secrets in environment variables or secret managers, not source code.
- Reason: Reduces risk of credential leakage.

### Logging and Monitoring
- Log security-relevant events without logging sensitive secrets.
- Reason: Helps detect and investigate attacks.

### Dependency Updates
- Patch vulnerable libraries and frameworks quickly.
- Reason: Many real-world breaches start from known vulnerable dependencies.

### Security Headers
- Use headers such as `Content-Security-Policy`, `X-Frame-Options`, and `Strict-Transport-Security` where appropriate.
- Reason: Adds browser-side protection layers.

## Common Injection Vulnerabilities

### SQL Injection
- **Definition:** Malicious input changes the meaning of SQL queries.
- **Prevention:** Use parameterized queries or ORM protections; never build SQL with raw string concatenation.

### Command Injection
- **Definition:** Untrusted input is executed by the operating system shell.
- **Prevention:** Avoid shell execution when possible; pass arguments safely and validate inputs.

### Cross-Site Scripting (XSS)
- **Definition:** Untrusted content executes as JavaScript in the browser.
- **Prevention:** Escape output, sanitize rich text, and use CSP where appropriate.

### NoSQL Injection
- **Definition:** Malicious input alters NoSQL query behavior.
- **Prevention:** Validate structure and use safe query builders.

### Template Injection
- **Definition:** User input is interpreted as template code.
- **Prevention:** Never evaluate untrusted template content.

### Why It Matters
Injection flaws can lead to data theft, account takeover, remote code execution, or full system compromise.

## Authentication Hardening

### Important Practices
- Hash passwords with modern password hashing algorithms.
- Enforce MFA for sensitive systems where possible.
- Limit login attempts and alert on suspicious activity.
- Revoke stolen or expired credentials quickly.

### Why It Matters
Authentication is one of the most attacked parts of any backend system.
