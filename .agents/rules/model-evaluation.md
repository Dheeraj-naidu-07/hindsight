---
trigger: model_decision
name: model-evaluation-rules
description: Apply when evaluating model performance, constructing golden datasets, using LLM-as-a-judge, or performing regression testing.
---

# Model Evaluation Rules

- **Evaluation Datasets**: Maintain curated datasets (golden datasets) of known inputs and correct outputs for consistent evaluation.
- **Objective Metrics**: Prefer objective, automated metrics (e.g., F1, exact match, rouge, NDCG) whenever possible to eliminate subjective variance.
- **Qualitative Evaluation**: When objective metrics are insufficient (e.g., for generation tone or style), use structured qualitative evaluation (human-in-the-loop or LLM-as-a-judge with strict rubrics).
- **Regression Testing**: Treat evaluations like unit tests. A drop in performance on the golden dataset should block deployment.
- **Edge Cases**: Include hard edge cases, adversarial inputs, and out-of-distribution data in the evaluation set.
- **Failure-Case Analysis**: Do not just look at aggregated metrics. Inspect individual failure cases to understand *why* the model failed.
- **Reproducible Evaluation**: Ensure that evaluating the same model on the same dataset yields the exact same metrics every time.
