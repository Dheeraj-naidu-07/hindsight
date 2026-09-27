---
trigger: model_decision
name: agent-engineering-rules
description: Apply when implementing autonomous agents, tool-calling loops, multi-agent architectures, or agent state management.
---

# Agent Engineering Rules

- **Explicit Tool Contracts**: Define clear, explicit schemas for all tools provided to the agent.
- **Bounded Agent Loops**: Implement hard limits (e.g., maximum iterations or maximum execution time) to prevent uncontrolled recursion or infinite loops.
- **State Management**: Maintain explicit state/memory across agent loops. Do not rely entirely on the model's context window if state can be managed externally.
- **Failure Recovery**: Agents must gracefully handle tool failure, invalid arguments, or API timeouts, and be able to self-correct.
- **Tool-Call Validation**: Validate arguments parsed from the model before executing the underlying tool. Prevent destructive actions from invalid parameters.
- **Deterministic Components**: Offload predictable tasks (like math or strict formatting) to deterministic code tools rather than having the LLM attempt them.
- **Observability**: Log the agent's full trajectory, including intermediate thoughts, tool calls, and tool results, for debugging and evaluation.
