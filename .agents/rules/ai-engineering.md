---
trigger: model_decision
name: ai-engineering-rules
description: Apply when integrating foundational LLMs, crafting prompts, handling AI inference limits, and designing AI application layers.
---

# AI Engineering Rules

- **Model abstraction**: Do not hardcode specific model calls in business logic. Use abstractions/interfaces to wrap LLM providers.
- **Model selection**: Choose the smallest, fastest model capable of reliably performing the task to save cost and latency.
- **Inference**: Use streaming where possible for long-running generations to improve user experience.
- **Prompt management**: Version and store prompts separately from code (e.g., in a separate config or module). Treat them as configuration.
- **Structured outputs**: Prefer models that natively support JSON/structured outputs and provide a strict schema (e.g., JSON schema) when specific output shapes are required.
- **Input/output validation**: Validate inputs before passing to the model. Strongly validate and sanitize model outputs before using them in the application.
- **Hallucination mitigation**: Ground the model by providing relevant context (RAG) and instruct it to cite sources or refuse to answer if it doesn't know.
- **Retry strategies**: Implement exponential backoff for rate limits and transient errors from provider APIs.
- **Timeouts**: Always set explicit timeouts on LLM API calls.
- **Rate limits**: Respect API rate limits and implement application-side queuing if necessary.
- **Cost**: Monitor and log token usage. Implement hard caps for expensive operations.
- **Latency**: Measure time-to-first-token and total generation time.
- **Observability**: Log prompts, outputs, latency, tokens, and model configurations for every interaction (consider privacy).
- **Evaluation**: Implement automated evaluations (evals) against a test set of prompts to prevent regressions when modifying prompts or swapping models.
- **Reproducibility**: Set a low temperature (e.g., `0.0`) for deterministic tasks. Store model version and parameters used for each generation.
- **Model/version tracking**: Pin to specific model versions (e.g., `gpt-4o-2024-05-13`) rather than generic aliases (e.g., `gpt-4o`) for stability.
