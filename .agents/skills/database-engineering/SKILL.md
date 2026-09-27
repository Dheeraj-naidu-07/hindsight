---
name: database-engineering
description: Use this skill when designing database schemas, writing complex SQL queries, creating migrations, or optimizing database performance.
---

# Database Engineering

## When to Use

Use this skill when:
- Creating or modifying database tables.
- Writing migration scripts.
- Optimizing slow queries.
- Designing relationships and constraints.

## Workflow

1. **Schema Design**: Draw out the entity-relationship diagram mentally or physically.
2. **Normalization**: Normalize data to 3NF to avoid anomalies.
3. **Constraints Definition**: Add primary keys, foreign keys, unique constraints, and check constraints.
4. **Migration Creation**: Write up/down migration scripts using the project's migration tool.
5. **Query Formulation**: Write the queries and test them against realistic data volumes.
6. **Indexing**: Identify read patterns and add appropriate indexes to support them.

## Best Practices

- **Let the DB do the work**: Use the database for constraints and data integrity, not just the application layer.
- **Use Transactions**: Group logical multi-step writes into transactions to ensure atomicity.
- **Parameterized Queries**: Always use parameterized queries (via ORM or raw SQL driver) to prevent injection.

## Common Failure Modes

- N+1 query problems in application loops.
- Missing indexes on foreign keys or frequently filtered columns.
- Using `SELECT *` which fetches unnecessary data and breaks if columns change.

## Verification

- Run `EXPLAIN ANALYZE` on new queries to verify index usage.
- Ensure migration scripts can be applied (`up`) and reverted (`down`) cleanly.
