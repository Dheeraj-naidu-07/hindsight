---
name: debugging
description: Use this skill to systematically isolate, diagnose, and fix bugs in an existing codebase.
---

# Debugging

## When to Use

Use this skill when:
- Investigating an error report or stack trace.
- A test is failing unexpectedly.
- The system is exhibiting incorrect behavior.

## Workflow

1. **Information Gathering**: Collect logs, stack traces, and input variables.
2. **Reproduction**: Create a minimal reproducible example or write a failing test case.
3. **Isolation**: Use a binary search method (or debugger) to narrow down the exact line or module causing the issue.
4. **Root Cause Analysis**: Understand why the code fails. Is it bad data? A race condition? A logic error?
5. **Formulate Fix**: Write the minimal amount of code needed to fix the issue.
6. **Verification**: Run the failing test (it should now pass) and check for regressions.

## Best Practices

- **Don't Guess**: Never change code randomly hoping it will fix the bug. Prove the cause first.
- **Leave It Better**: If the bug was caused by poor readability or missing types, improve the surrounding code slightly while fixing it.
- **Add Tests**: A bug fixed without a test added is a bug that will return.

## Common Failure Modes

- Fixing the symptom (e.g., adding `if x is not None:`) rather than the root cause (e.g., why is `x` None in the first place?).
- Making massive refactors while trying to fix a small bug.

## Verification

- The test written in step 2 must pass.
- The rest of the test suite must also pass.
