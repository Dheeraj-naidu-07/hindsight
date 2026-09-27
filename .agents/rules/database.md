---
trigger: model_decision
name: database-rules
description: Apply when designing schemas, writing SQL/NoSQL queries, optimizing database performance, or working with migrations.
---

# Database Rules

- **PostgreSQL**: Prefer PostgreSQL as the default relational database unless specified otherwise.
- **Schema design**: Design schemas for read efficiency or write efficiency based on the primary access pattern.
- **Normalization**: Start with 3NF. Denormalize only when proven necessary for performance.
- **Constraints**: Use database constraints (NOT NULL, UNIQUE, CHECK, FOREIGN KEY) to enforce data integrity at the lowest level.
- **Relationships**: Define relationships clearly and use proper cascading rules.
- **Indexing**: Add indexes on foreign keys and frequently filtered/sorted columns. Avoid over-indexing to prevent write degradation.
- **Transactions**: Keep transactions short. Do not make external API calls inside a database transaction.
- **Isolation**: Understand transaction isolation levels and use them to prevent race conditions.
- **Migrations**: Use a migration tool (e.g., Alembic, Flyway). Never mutate schema manually in production.
- **Query optimization**: Use `EXPLAIN ANALYZE` for slow queries.
- **N+1 problems**: Always eager load or batch load related entities when querying lists.
- **Connection management**: Use connection pooling (e.g., PgBouncer) to prevent exhausting database connections.
- **Parameterized queries**: Always use parameterized queries (prepared statements) or ORMs to prevent SQL injection.
- **Data integrity**: Rely on the database as the single source of truth for relationships and integrity.
