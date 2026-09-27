---
trigger: model_decision
name: backend-engineering-rules
description: Apply when designing, implementing, debugging, or reviewing backend services, business logic, server-side architecture, or backend infrastructure.
---

# Backend Engineering Rules

- **Layered architecture**: Keep logic separated into appropriate layers (Routing, Business, Data).
- **Routes/controllers**: Controllers should only handle HTTP logic, validation, and calling services. No business logic in controllers.
- **Services**: All business logic goes here. Services can call other services or repositories.
- **Repositories**: Handle all data access. Abstract the database away from the service layer.
- **Models**: Define the core entity structures used across layers.
- **Schemas**: Use explicit schemas (e.g., Pydantic) for validation and serialization.
- **Dependency injection**: Inject dependencies (e.g., db sessions, clients) instead of hardcoding them to make testing easier.
- **Validation**: Validate all inputs at the boundary. Fail fast on bad data.
- **Authentication**: Verify identity before processing sensitive requests.
- **Authorization**: Verify permissions/roles before allowing access to resources.
- **Error handling**: Use centralized exception handlers to format standard API error responses.
- **Logging**: Log at appropriate levels (INFO, WARN, ERROR). Do not log PII or secrets. Include request correlation IDs.
- **Transactions**: Wrap multi-step database mutations in a transaction. Ensure atomic commits/rollbacks.
- **Idempotency**: Design state-mutating endpoints (especially POST/PUT) to be safely retried.
- **Background jobs**: Offload long-running tasks to queues/workers (e.g., Celery) rather than blocking the web thread.
- **External services**: Always use timeouts and retries for external API calls. Handle failures gracefully.
- **Scalability**: Build stateless backend servers to allow horizontal scaling.

*Note on frameworks*: Use Python/FastAPI conventions (Pydantic, Dependency Injection, async/await) as a standard reference, but do not force FastAPI onto unrelated projects.
