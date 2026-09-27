---
name: ai-engineering
description: Use this skill when integrating LLMs, designing prompts, handling model inference, or building RAG/agentic workflows.
---

# AI Engineering

## When to Use

Use this skill when:
- Writing or optimizing prompts.
- Integrating a new LLM provider or model.
- Building Retrieval-Augmented Generation (RAG) pipelines.
- Parsing unstructured outputs into structured data (e.g., JSON).

## Workflow

1. **Model Selection**: Choose the right model based on cost, latency, and capability requirements.
2. **Prompt Engineering**: Draft clear, context-rich prompts with explicit instructions and formatting constraints.
3. **Integration**: Wrap the model call in a resilient client with timeouts, retries, and error handling.
4. **Validation**: Validate the model's output against a strict schema.
5. **Evaluation**: Test the prompt/model combination against a benchmark dataset of typical inputs.

## Best Practices

- **Structured Outputs**: Force JSON output (via tools or JSON mode) and validate it with a schema library (like Pydantic/Zod) before using it.
- **Provide Context**: Give the model specific, bounded context to reduce hallucination.
- **Separate Config**: Keep prompts out of core logic; store them as templates.

## Common Failure Modes

- Assuming the model's output will always be correctly formatted or accurate.
- Failing to handle provider rate limits (429) or timeouts (504).
- Using the most expensive/capable model for trivial tasks that a smaller model could handle.

## Verification

- Verify that output validation catches hallucinations or bad formatting without crashing the application.
- Ensure latency and cost are monitored for every inference call.
