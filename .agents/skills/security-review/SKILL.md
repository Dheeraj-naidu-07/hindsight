---
name: security-review
description: Use this skill to perform dedicated security audits on code, infrastructure, and API design to identify vulnerabilities.
---

# Security Review

## When to Use

Use this skill when:
- Auditing authentication and authorization logic.
- Reviewing endpoints that handle sensitive user data (PII).
- Checking for injection vulnerabilities or misconfigurations.
- Performing a threat modeling exercise.

## Workflow

1. **Identify the Assets**: Determine what data or functionality is most critical to protect.
2. **Trace the Boundaries**: Follow data from untrusted sources (users, external APIs) into the system.
3. **Audit Authentication**: Verify that identity is established securely (no home-rolled crypto, proper session management).
4. **Audit Authorization**: Verify that every endpoint checks permissions/ownership before acting.
5. **Input Validation**: Check that all input is sanitized, type-checked, and length-limited.
6. **Output Encoding**: Ensure data returned to the user or database is properly escaped/parameterized.

## Best Practices

- **Assume Breach**: Design systems so that if one component is compromised, the blast radius is limited (defense in depth).
- **Default Deny**: APIs should reject requests unless explicitly permitted.
- **Fail Securely**: If an error occurs, the system should not leak state or elevate privileges.

## Common Failure Modes

- Trusting client-side validation without repeating it on the server.
- Logging sensitive information (passwords, tokens, PII) in plain text.
- Using outdated dependencies with known CVEs.

## Verification

- Verify that automated SAST (Static Application Security Testing) tools would not flag the code.
- Ensure secrets are loaded via environment variables and never hardcoded.
