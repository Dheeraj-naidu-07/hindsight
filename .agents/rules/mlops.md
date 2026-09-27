---
trigger: model_decision
name: mlops-rules
description: Apply when tracking ML experiments, managing model registries, building CI/CD ML pipelines, or monitoring model drift in production.
---

# MLOps Rules

- **Experiment Tracking**: Log all training runs, parameters, metrics, and data versions in an experiment tracking system (e.g., MLflow, Weights & Biases).
- **Model Lifecycle**: Explicitly manage models through staging, production, and archived states via a Model Registry.
- **Reproducible Pipelines**: Training, evaluation, and deployment must be automated via code (CI/CD for ML), requiring no manual intervention.
- **Monitoring**: Continuously monitor model performance in production (latency, error rates, resource usage).
- **Data and Model Drift**: Implement checks to detect when incoming data distributions change (data drift) or model performance degrades over time (concept drift).
- **Rollback Strategy**: Always have an automated mechanism to roll back to the previously deployed model if the new version fails or degrades.
- **Artifact Management**: Store model weights, tokenizers, and dependencies as immutable artifacts.
