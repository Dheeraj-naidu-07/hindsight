---
trigger: model_decision
name: code-review-rules
description: Apply when reviewing code for correctness, security, performance, maintainability, or preparing a pull request.
---

# Code Review Rules

Review code in this specific order of priority:

1. **Correctness**: Does the code do what it is supposed to do? Are there logic errors?
2. **Security**: Are there vulnerabilities (e.g., injection, unauthorized access, exposed secrets)?
3. **Data integrity**: Could this change corrupt data or leave the database in an inconsistent state?
4. **API compatibility**: Does this break existing API contracts or frontend expectations?
5. **Error handling**: Are exceptions caught? Are errors logged properly and returned gracefully?
6. **Performance**: Are there N+1 query problems, missing indexes, or unnecessary memory allocations?
7. **Maintainability**: Is the code modular, DRY, and easy to modify in the future?
8. **Testing**: Are there sufficient tests for the new logic? Do the tests actually assert the correct behavior?
9. **Readability**: Are variables named well? Is the code easy to understand at a glance?
10. **Documentation**: Are comments, docstrings, and READMEs updated to reflect the changes?
