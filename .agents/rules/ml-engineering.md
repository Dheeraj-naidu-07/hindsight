---
trigger: model_decision
name: ml-engineering-rules
description: Apply when working on machine-learning datasets, feature engineering, model training, validation, experimentation, or inference pipelines.
---

# Machine Learning Engineering Rules

- **Reproducibility**: Set seeds for all random number generators. Document exact hardware, library versions, and data snapshots used for training.
- **Train/Validation/Test Separation**: Maintain strict separation. The test set must be held out completely until final model evaluation.
- **Leakage Prevention**: Ensure no target variables or future data leak into the training features.
- **Baseline Models**: Always establish a simple baseline (e.g., heuristic, linear regression, or random forest) before training complex models.
- **Meaningful Metrics**: Choose evaluation metrics that reflect business value (e.g., F1-score for imbalanced classes, not just accuracy).
- **Error Analysis**: Systematically analyze false positives and false negatives to understand model blind spots.
- **Experiment Tracking**: Track all hyperparameters, metrics, and code versions for every experiment.
- **Model/Version Tracking**: Version control model artifacts alongside the data and code that produced them.
