---
trigger: model_decision
name: testing-rules
description: Apply when writing or reviewing unit tests, integration tests, E2E tests, or testing strategies.
---

# Testing Rules

- **Unit testing**: Write isolated tests for individual functions and classes. Mock external dependencies.
- **Integration testing**: Test how multiple components (or the database) interact together.
- **API testing**: Write end-to-end tests for critical API routes, ensuring request/response schemas and status codes are correct.
- **Database testing**: Use a test database. Setup and teardown test data for each test suite.
- **AI evaluation**: Use automated evals for LLM prompts to ensure response quality and format consistency.
- **Data pipeline testing**: Test transformations with known input/output pairs.
- **Regression testing**: Whenever a bug is fixed, write a test that would have caught it.
- **Edge cases**: Test boundary values, nulls, empty lists, and unusually large inputs.
- **Failure cases**: Explicitly test how the system behaves when dependencies fail or inputs are invalid.
- **Test quality**: Tests should be deterministic (no flaky tests) and fast. A test should fail if and only if the code is broken.
