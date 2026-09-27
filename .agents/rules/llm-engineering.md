---
trigger: model_decision
name: llm-engineering-rules
description: Apply when structuring LLM outputs, defining schemas, managing rate-limits, and configuring deterministic models.
---

# LLM Engineering Rules

- **Structured Outputs**: Use structured outputs where appropriate. Define explicit schemas (e.g., JSON schema) for expected outputs.
- **Model Abstraction**: Do not hardcode specific model API endpoints deep within logic. Use abstraction layers.
- **Timeouts and Retries**: Always set timeouts for model calls. Implement retry strategies for transient errors.
- **Rate-limit Handling**: Handle HTTP 429 status codes gracefully, utilizing backoff mechanisms.
- **Cost and Token Awareness**: Be aware of token consumption limits. Monitor and limit generation length based on cost constraints.
- **Latency Awareness**: Utilize streaming generation when latency is critical for user experience.
- **Deterministic Settings**: Use deterministic settings (e.g., temperature = 0) when appropriate (e.g., for extraction or classification tasks).
- **Model and Version Tracking**: Track specific model versions (e.g., `gpt-4-0613` or `claude-3-opus-20240229`) rather than using rolling tags to ensure reproducible outputs.
- **Validation**: Validate all model outputs against the expected schema before downstream processing.
