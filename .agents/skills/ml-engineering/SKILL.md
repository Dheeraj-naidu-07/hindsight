---
name: ml-engineering
description: Use this skill when preparing datasets, extracting features, training models, or running machine learning experiments.
---

# Machine Learning Engineering

## When to Use

Use this skill when:
- Writing feature engineering pipelines.
- Training supervised or unsupervised machine learning models.
- Tuning hyperparameters.
- Performing error analysis on a trained model.

## Workflow

1. **Data Prep**: Split data into strictly non-overlapping train, validation, and test sets.
2. **Feature Engineering**: Impute missing values, scale numerical features, encode categoricals.
3. **Baseline**: Train a naive baseline model (e.g., linear regression or random forest) to establish a floor for performance.
4. **Training**: Train the primary model, evaluating against the validation set.
5. **Tuning**: Tune hyperparameters using cross-validation.
6. **Evaluation**: Perform a final evaluation on the held-out test set.

## Best Practices

- Prevent data leakage: any scaler or imputer must be fit *only* on the training data.
- Always set random seeds for reproducibility.

## Common Failure Modes

- Leaking the target variable into the training features.
- Evaluating the model on the same data it was trained on, leading to severe overfitting.

## Verification

- Ensure that a dummy model (e.g., always predicting the majority class) performs significantly worse than your trained model.
