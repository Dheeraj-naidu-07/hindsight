---
name: mlops
description: Use this skill when setting up experiment tracking, model registries, CI/CD for ML, or model monitoring pipelines.
---

# MLOps

## When to Use

Use this skill when:
- Instrumenting code with experiment tracking (e.g., MLflow).
- Managing model lifecycles and artifact storage.
- Building reproducible deployment pipelines for models.
- Setting up data drift or model drift monitoring.

## Workflow

1. **Tracking**: Integrate a tracking library to log hyperparameters, metrics, and artifacts during training.
2. **Registry**: Register the best performing models in a central model registry.
3. **Packaging**: Package the model, its dependencies, and inference code into a container or deployable artifact.
4. **Deployment**: Deploy the model (batch, streaming, or REST endpoint).
5. **Monitoring**: Collect live predictions and ground truth (when available) to monitor for drift.

## Best Practices

- Tie every deployed model back to the exact code commit and data snapshot that produced it.
- Automate the training and deployment pipeline; manual model handoffs are prone to error.

## Common Failure Modes

- "Works on my machine": Failing to pin library versions, resulting in inference failing in production.
- Concept drift: The world changes, but the model is never retrained, leading to silent performance degradation.

## Verification

- Ensure you can pull the model artifact from the registry and run inference in an isolated environment successfully.
