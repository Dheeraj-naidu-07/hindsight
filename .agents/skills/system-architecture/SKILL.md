---
name: system-architecture
description: Use this skill when designing the high-level components of a system, choosing technologies, or evaluating trade-offs in distributed systems.
---

# System Architecture

## When to Use

Use this skill when:
- Designing a new system from scratch.
- Breaking a monolith into microservices.
- Choosing a database, messaging queue, or caching layer.
- Evaluating system scalability and resilience.

## Workflow

1. **Requirements Gathering**: Collect functional and non-functional requirements (scale, latency, availability).
2. **Component Design**: Break the system into logical components (e.g., API gateway, auth service, database).
3. **Data Flow**: Map how data moves through the system (synchronous REST, asynchronous events).
4. **Technology Selection**: Choose the right tools for the job based on constraints.
5. **Trade-off Analysis**: Explicitly document trade-offs (e.g., consistency vs. availability).
6. **Documentation**: Create architecture diagrams and write design documents.

## Best Practices

- **Keep It Simple**: Start with a simple, monolithic architecture unless scale dictates otherwise.
- **Design for Failure**: Assume networks will partition, servers will crash, and databases will go down. Use retries and circuit breakers.
- **Loose Coupling**: Components should communicate via well-defined APIs or events, minimizing shared state.

## Common Failure Modes

- Over-engineering for Google-scale when the product only has 100 users.
- Premature optimization (e.g., implementing microservices without understanding domain boundaries).
- Creating a distributed monolith where services are so tightly coupled they must be deployed together.

## Verification

- The design must explicitly address the non-functional requirements (e.g., "How does this handle 10k RPS?").
- Ensure a clear migration path exists if replacing an older system.
