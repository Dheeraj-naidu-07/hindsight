---
name: agent-engineering
description: Use this skill when designing autonomous AI agents, multi-agent systems, or orchestrating tool-calling loops.
---

# Agent Engineering

## When to Use

Use this skill when:
- Creating loops where an LLM decides which tools to call dynamically.
- Designing multi-agent architectures or workflows (e.g., planner/executor).
- Implementing state management across multiple LLM turns.

## Workflow

1. **Tool Definition**: Define clear, heavily documented schemas for all tools the agent can use.
2. **System Prompt**: Write a system prompt giving the agent a persona, constraints, and instructions on how to use its tools.
3. **The Loop**: Implement the core agent loop: Generate -> Execute Tool -> Append Result -> Repeat.
4. **State Management**: Maintain memory (short-term conversation history, long-term semantic memory).
5. **Exit Conditions**: Define strict exit criteria (goal achieved, max steps reached, or fatal error).

## Best Practices

- Tools should validate their own inputs and return clear, stringified error messages if validation fails, so the LLM can self-correct.
- Enforce a maximum number of tool calls or iterations to prevent infinite loops.

## Common Failure Modes

- Agent getting stuck in an infinite loop trying the same failing tool call repeatedly.
- Providing too many tools, overwhelming the model's ability to choose correctly.

## Verification

- Trace the agent's trajectory for a complex task to ensure it plans correctly and uses tools as intended.
