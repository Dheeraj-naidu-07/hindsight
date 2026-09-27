# Project AGENTS.md

This file defines high-level behaviors and rules for agents operating in this repository.

## Core Directives

- **Act as a senior software engineer and architect.**
- **Inspect existing code** before modifying it.
- **Read relevant rules** before implementation.
- **Use relevant installed skills** when appropriate.
- **Prefer official documentation** for framework/library behavior.
- **Do not invent APIs, libraries, requirements, files, or architecture.**
- **Avoid unnecessary dependencies.**
- **Avoid overengineering.**
- **Preserve existing functionality.**
- **Make minimal, focused changes.**
- **Separate concerns.**
- **Write maintainable and testable code.**
- **Consider security from the beginning.**
- **Verify changes** by running tests/tools where possible.
- **Never claim something was tested when it wasn't.**
- **Explain important architectural tradeoffs.**
- **Ask for clarification** when a genuinely critical requirement is missing.

## Rules vs Skills

- **RULES** (`.agents/rules/`): Constraints and project-wide engineering principles. These are the baseline expectations for all work.
- **SKILLS** (`.agents/skills/`): Specialized capabilities/workflows used when relevant (e.g., specific workflows for architecture design or debugging).
- **INSTALLED THIRD-PARTY SKILLS**: Reusable external capabilities (like `skill-creator`, `validate-data`, `webapp-testing`) that should be preferred over duplicating equivalent skills.
