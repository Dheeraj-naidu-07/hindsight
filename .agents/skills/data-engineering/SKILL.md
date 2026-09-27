---
name: data-engineering
description: Use this skill when building data pipelines, writing ETL/ELT jobs, designing data warehouses, or processing large datasets.
---

# Data Engineering

## When to Use

Use this skill when:
- Creating data extraction, transformation, and loading (ETL/ELT) processes.
- Designing data warehouse schemas (e.g., star schema).
- Processing large batches or streams of data.
- Implementing data quality checks within a pipeline.

## Workflow

1. **Source Analysis**: Understand the schema, volume, and velocity of the source data.
2. **Pipeline Design**: Determine if the pipeline should be batch or streaming.
3. **Extraction**: Connect to the source and extract data robustly, handling pagination and rate limits.
4. **Transformation**: Clean, cast types, and map data to the target schema.
5. **Loading**: Use bulk insert or optimized loading mechanisms for the destination.
6. **Orchestration**: Schedule the job and define dependencies.

## Best Practices

- **Idempotency**: A pipeline should be able to run multiple times on the same interval without duplicating data.
- **Fail Fast**: Validate early in the pipeline so corrupted data doesn't poison downstream tables.
- **Documentation**: Document data lineage so consumers know where a metric originated.

## Common Failure Modes

- OOM (Out of Memory) errors from loading an entire dataset into memory instead of streaming/chunking.
- Silently ignoring errors, leading to incomplete data in the warehouse.
- Changing schemas upstream that break the extraction logic downstream.

## Verification

- Run a subset of data through the pipeline and verify output against expected transformations.
- Check that the `validate-data` skill criteria pass for the resulting datasets.
