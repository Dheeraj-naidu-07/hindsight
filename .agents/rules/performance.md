---
trigger: model_decision
name: performance-rules
description: Apply when optimizing code performance, profiling bottlenecks, or managing system resources efficiently.
---

# Performance Rules

- **Measure before optimizing**: Do not guess where the bottleneck is. Use profiling tools to find it.
- **Profiling**: Profile CPU, memory, and I/O before committing to a complex optimization.
- **Database performance**: Focus on the database first. Slow queries account for the majority of performance issues.
- **Query optimization**: Add missing indexes, avoid `SELECT *`, and use `EXPLAIN ANALYZE`.
- **Caching**: Cache expensive, frequently requested, and infrequently changing data (e.g., using Redis).
- **Async I/O**: Use asynchronous operations for network and disk I/O to avoid blocking the main execution thread.
- **CPU/memory**: Avoid loading entire large datasets into memory. Use streaming, generators, or chunking.
- **Network latency**: Batch API requests. Minify and compress payloads where appropriate.
- **AI inference latency**: Use streaming for LLM outputs. Precompute or use smaller models where latency is critical.
- **Cost optimization**: Monitor infrastructure costs. Turn off idle resources. Optimize token usage in LLM calls.
