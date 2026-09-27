---
name: llm-engineering
description: Use this skill when building or refactoring applications powered by Large Language Models, including managing inference, contexts, and integrations.
---

# LLM Engineering

## When to Use

Use this skill when:
- Developing applications that rely on LLM APIs.
- Managing context windows and prompt construction.
- Structuring LLM outputs for deterministic downstream use.

## Workflow

1. **Model Selection**: Choose a model balancing latency, cost, and intelligence.
2. **Context Management**: Assemble the prompt dynamically, ensuring strict separation of instructions and user data.
3. **API Integration**: Wrap the API call with retry logic, timeouts, and rate-limit handling.
4. **Structured Outputs**: Force the LLM to return JSON (or another structured format) and parse it securely.
5. **Validation**: Validate the parsed output against a rigid schema.

## Best Practices

- Always abstract the LLM provider (e.g., use an interface) so you can swap models without rewriting business logic.
- Use tools/function calling for structured outputs when available.

## Common Failure Modes

- Prompt injection vulnerabilities from unescaped user inputs.
- Brittle regex parsing of LLM outputs instead of using native structured output modes.
- Failing to account for token limits, causing the API to reject the request or truncate the output.

## Verification

- Confirm that invalid outputs from the LLM are caught by validation and trigger a retry or fallback.
