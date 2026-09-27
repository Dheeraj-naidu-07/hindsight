---
trigger: always_on
---

# Security Rules

- **Secrets**: Never hardcode API keys, passwords, or tokens. Use environment variables or a secret manager.
- **Authentication**: Require strong authentication. Do not roll your own crypto or auth protocols; use established libraries.
- **Authorization**: Enforce access controls on every sensitive endpoint and resource. Default to deny.
- **Input validation**: Validate all untrusted input against strict allowlists (types, lengths, formats).
- **SQL injection**: Always use parameterized queries or ORMs. Never concatenate strings into SQL.
- **Command injection**: Avoid `system()` or `exec()` with user input. If required, sanitize heavily and use safe execution methods.
- **SSRF**: Prevent Server-Side Request Forgery by strictly validating URLs before making backend requests to them.
- **Path traversal**: Sanitize file paths. Ensure user input cannot navigate outside intended directories (`../`).
- **Sensitive-data exposure**: Hash passwords (e.g., bcrypt/Argon2). Encrypt sensitive PII at rest and in transit (TLS).
- **Dependency security**: Regularly scan and update dependencies for known vulnerabilities.
- **Logging security**: Never log secrets, passwords, or full credit card numbers. Redact PII.
- **Error disclosure**: Do not leak stack traces or internal server errors to the client in production. Return generic error messages.
- **Least privilege**: Run services and database connections with the minimum permissions necessary.
