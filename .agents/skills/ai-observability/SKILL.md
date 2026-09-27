---
name: ai-observability
description: Use this skill when implementing telemetry, tracing, logging, or monitoring for AI systems and LLM calls in production.
---

# AI Observability

## When to Use

Use this skill when:
- Tracking LLM token usage and costs.
- Tracing execution paths of complex agentic workflows.
- Capturing user feedback on model generations.
- Diagnosing latency issues in production AI apps.

## Workflow

1. **Instrumentation**: Integrate an observability SDK (e.g., LangSmith, Phoenix, or OpenTelemetry).
2. **Tracing**: Wrap core components (Retrievers, LLM calls, Tools) in traces.
3. **Metadata**: Attach crucial metadata (user ID, session ID, model name, prompt version) to every trace.
4. **Feedback Loop**: Expose a way for end-users to rate outputs (thumbs up/down) and join this data to the traces.
5. **Dashboarding**: Create monitors for p99 latency, cost spikes, and error rates.

## Best Practices

- Do not log Personally Identifiable Information (PII) or sensitive customer data in traces without redaction.
- Log both the exact input prompt and the exact output generation for debugging.

## Common Failure Modes

- Tracing overhead significantly slowing down the user experience.
- Losing the correlation between a user's initial request and a deep sub-agent's API call.

## Verification

- Ensure that a single request generates a complete, connected trace tree in the observability backend.
