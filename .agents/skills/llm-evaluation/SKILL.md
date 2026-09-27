---
name: llm-evaluation
description: Use this skill when creating automated regression tests, benchmarks, or LLM-as-a-judge pipelines for language models.
---

# LLM Evaluation

## When to Use

Use this skill when:
- Testing if a prompt change degraded performance.
- Comparing two different LLM providers or models.
- Validating the faithfulness or relevance of RAG responses.

## Workflow

1. **Dataset Creation**: Build a "golden dataset" of inputs and expected outputs (or expected facts).
2. **Metric Selection**: Choose metrics (e.g., exact match, JSON validity, semantic similarity, or LLM-as-a-judge).
3. **Execution**: Run the model over the dataset and collect outputs.
4. **Scoring**: Apply the selected metrics to the outputs.
5. **Analysis**: Review the aggregate scores and deeply inspect the failing examples.

## Best Practices

- Treat evaluations as code: version control the evaluation datasets and scoring logic.
- When using LLM-as-a-judge, use a stronger, more capable model (e.g., Claude 3.5 Sonnet or Opus) to judge the outputs of a faster model.

## Common Failure Modes

- Overfitting the prompt to the golden dataset so it fails in production.
- Using LLM-as-a-judge with a vague rubric, leading to highly variant and unreliable scores.

## Verification

- Verify that your LLM-as-a-judge correlates with human judgment on a sample of outputs.
