---
name: api-design
description: Use this skill when planning new API endpoints, designing RESTful contracts, or defining data schemas for communication between clients and servers.
---

# API Design

## When to Use

Use this skill when:
- Creating a new API endpoint.
- Designing a new microservice interface.
- Defining request/response payloads.
- Planning API versioning strategies.

## Workflow

1. **Resource Identification**: Identify the core nouns (resources) being exposed.
2. **Method Assignment**: Map CRUD operations to correct HTTP methods (GET, POST, PUT, PATCH, DELETE).
3. **Schema Definition**: Define strict JSON schemas for input and output, including error states.
4. **Path Structuring**: Design clean, hierarchical URLs (e.g., `/users/{id}/orders`).
5. **Documentation**: Generate or write OpenAPI/Swagger specifications.

## Best Practices

- **Use Plural Nouns**: Use `/resources` instead of `/resource`.
- **Status Codes**: Use the full range of HTTP status codes appropriately (e.g., 400 for bad input, 404 for not found, 403 for unauthorized).
- **Pagination & Filtering**: Always design list endpoints with pagination (offset/limit or cursors) and filtering capabilities from the start.

## Common Failure Modes

- Leaking internal database models directly as API responses.
- Using POST for everything instead of the appropriate HTTP method.
- Making breaking changes (e.g., removing a field) without versioning the API.

## Verification

- Ensure the API documentation matches the implemented schema exactly.
- Verify that bad inputs return a 400 status with clear, actionable validation error messages.
