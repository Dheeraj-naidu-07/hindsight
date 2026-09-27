---
trigger: model_decision
name: debugging-rules
description: Apply when investigating bugs, analyzing logs, handling stack traces, or fixing runtime errors.
---

# Debugging Rules

When encountering an issue, follow this strict procedure. Do not encourage random code changes or "guess and check" programming.

1. **Reproduce**: Consistently reproduce the error in a controlled environment.
2. **Isolate**: Narrow down the system, component, or specific function where the error occurs.
3. **Inspect evidence**: Read logs, stack traces, variable states, and documentation to understand exactly what is failing.
4. **Identify root cause**: Determine *why* the failure happens, not just *where*.
5. **Make minimal fix**: Write the smallest, safest change that resolves the root cause.
6. **Test**: Run unit tests or reproduce the original scenario to prove the fix works.
7. **Verify**: Ensure that the fix did not cause collateral damage (regressions) in related systems.
