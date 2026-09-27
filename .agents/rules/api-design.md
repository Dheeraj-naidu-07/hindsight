---
trigger: model_decision
name: api-design-rules
description: Apply when planning, designing, documenting, or modifying API contracts, endpoints, schemas, and RESTful architectures.
---

# API Design Rules

- **REST**: Follow RESTful conventions. Use nouns for endpoints, not verbs (e.g., `/users` not `/getUsers`).
- **HTTP methods**: Use GET for reading, POST for creation, PUT for full replacement, PATCH for partial updates, and DELETE for deletion.
- **Status codes**: Return accurate HTTP status codes (200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Internal Server Error).
- **Request/response schemas**: Define clear, consistent JSON schemas for all inputs and outputs.
- **Validation**: Reject invalid requests immediately with a 400 status and detailed validation errors.
- **Pagination**: Always paginate endpoints that return lists. Use cursor or offset-based pagination.
- **Filtering**: Support filtering via query parameters (e.g., `?status=active`).
- **Sorting**: Support sorting via query parameters (e.g., `?sort=-created_at`).
- **Errors**: Return a consistent error structure (e.g., `{"error": "message", "details": []}`).
- **Authentication**: Require valid tokens for all protected routes.
- **Authorization**: Ensure the authenticated user owns or has permission to access the requested resource.
- **Versioning**: Version the API (e.g., `/v1/users`) from the beginning.
- **Backward compatibility**: Never remove fields or change types in existing endpoints. Add new fields or create a new version.
- **Documentation**: Provide OpenAPI/Swagger documentation for all endpoints.
- **Rate limiting**: Apply rate limits to prevent abuse and ensure stability.
