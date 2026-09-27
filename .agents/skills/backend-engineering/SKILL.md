---
name: backend-engineering
description: Use this skill when designing or implementing backend services, setting up project structures, or adding new business logic layers.
---

# Backend Engineering

## When to Use

Use this skill when:
- Creating a new backend project or service.
- Refactoring business logic.
- Adding new layers (e.g., controllers, services, repositories).
- Implementing background jobs or asynchronous processing.

## Workflow

1. **Understand Requirements**: Clarify the business problem and required data models.
2. **Design the Architecture**: Decide on the separation of concerns (e.g., MVC, clean architecture).
3. **Define Interfaces**: Draft the interfaces/abstract classes for repositories and services before implementation.
4. **Implement Core Logic**: Write the domain/service logic independent of the web framework.
5. **Implement Adapters**: Write controllers and database repositories to integrate with the core logic.
6. **Wire Dependencies**: Setup dependency injection.

## Best Practices

- **Dependency Injection**: Never hardcode dependencies; inject them to facilitate testing.
- **Statelessness**: Keep web servers stateless to allow horizontal scaling.
- **Fat Services, Skinny Controllers**: Controllers should only parse HTTP requests and format responses. Services do the real work.

## Common Failure Modes

- Tight coupling between the web framework and business logic.
- Blocking the main thread with long-running synchronous operations (like network calls or heavy processing).
- Ignoring transaction boundaries across multiple database updates.

## Verification

- Ensure unit tests can be written for services without needing a running database or web server.
- Verify that background jobs are properly enqueued and processed outside the main web thread.
