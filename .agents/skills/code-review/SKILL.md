---
name: code-review
description: Use this skill to review code for correctness, security, performance, and maintainability before it is merged.
---

# Code Review

## When to Use

Use this skill when:
- Reviewing a Pull Request or a diff.
- Evaluating a proposed architectural change.
- Performing a self-review before committing.

## Workflow

1. **Understand the Goal**: Read the PR description or issue to understand what the code *should* do.
2. **High-Level Review**: Check architectural decisions, API contracts, and database schema changes.
3. **Logic Review**: Trace the execution path. Look for edge cases, off-by-one errors, and unhandled exceptions.
4. **Security Review**: Check for common vulnerabilities (SQL injection, XSS, exposed secrets, auth bypass).
5. **Performance Review**: Look for N+1 queries, memory leaks, and inefficient algorithms.
6. **Style and Maintainability**: Ensure naming is clear, code is DRY, and tests are included.

## Best Practices

- **Be Constructive**: Focus on the code, not the author. Suggest concrete alternatives.
- **Prioritize**: Distinguish between blocking issues (bugs, security) and nitpicks (style).
- **Check Tests**: Code without tests (or with useless tests) should rarely pass review.

## Common Failure Modes

- "LGTM" (Looks Good To Me) rubber-stamping without actually reading the code.
- Focusing entirely on formatting and ignoring massive logic flaws.
- Missing edge cases because the "happy path" looks correct.

## Verification

- Ensure every comment or finding is tied to a specific line of code or architectural rule.
- Verify that the tests actually cover the new logic.
