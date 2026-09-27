---
name: prompt-engineering
description: Use this skill when writing, refining, or versioning prompts for Large Language Models to improve accuracy, formatting, or reasoning.
---

# Prompt Engineering

## When to Use

Use this skill when:
- Creating instructions for a new LLM task.
- Fixing a prompt that frequently hallucinates or produces malformed output.
- Implementing few-shot examples or Chain-of-Thought (CoT).

## Workflow

1. **Define the Goal**: Clearly state the role, task, and desired output format.
2. **Structure the Prompt**: Use clear boundaries (e.g., XML tags or Markdown) to separate instructions from input data.
3. **Add Examples**: Provide 1-3 high-quality input/output pairs (few-shot prompting).
4. **Enforce Reasoning**: If the task is complex, instruct the model to output its reasoning (e.g., inside `<thought>` tags) *before* the final answer.
5. **Iterate**: Test the prompt against failure cases and refine.

## Best Practices

- Be explicit and direct. Avoid polite filler.
- Tell the model what *to* do, rather than what *not* to do.
- Keep prompts versioned alongside the code.

## Common Failure Modes

- "Prompt drift": A prompt optimized for one model performs poorly when the underlying model is upgraded.
- Burying the most important instruction in the middle of a massive block of text.

## Verification

- Test the prompt on at least 5 varied inputs to ensure consistent formatting and logic.
