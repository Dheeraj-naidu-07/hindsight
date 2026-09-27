---
trigger: always_on
---

# General Engineering Rules

- **Clean code**: Code must be easy to read and understand. Name variables and functions clearly.
- **Modularity**: Break down complex problems into smaller, manageable, and testable modules.
- **Separation of concerns**: Ensure that different sections of code handle different parts of the application logic.
- **KISS (Keep It Simple, Stupid)**: Avoid complex solutions when simple ones will do.
- **DRY (Don't Repeat Yourself)**: Extract duplicated logic into reusable functions or components.
- **YAGNI (You Aren't Gonna Need It)**: Do not add functionality until it is absolutely necessary.
- **SOLID**: Apply SOLID principles when appropriate to maintain object-oriented design quality.
- **Maintainability**: Write code with the assumption that someone else will have to maintain it.
- **Readability**: Prioritize readable code over clever, compact code.
- **Error handling**: Handle errors gracefully. Provide meaningful error messages and fail safely.
- **Configuration**: Extract configuration variables (e.g., environment variables) out of the codebase.
- **Dependency management**: Keep dependencies up to date and minimize the number of external packages.
- **Documentation**: Document the "why" in comments, not just the "what". Ensure READMEs are kept current.
- **Backward compatibility**: Do not break existing consumers without a deprecation plan.
- **Avoiding unnecessary abstractions**: Do not abstract code unless there is a proven need for reuse or testing.
