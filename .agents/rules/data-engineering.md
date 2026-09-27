---
trigger: model_decision
name: data-engineering-rules
description: Apply when building data pipelines, ETL processes, data warehouses, or processing large datasets.
---

# Data Engineering Rules

- **Ingestion**: Ensure data ingestion is idempotent. Handle duplicate data gracefully.
- **Validation**: Validate incoming data schemas and types before processing. Use tools like `validate-data` for methodological checks.
- **Cleaning**: Standardize formats (e.g., dates to UTC, strings to lowercase/trimmed) early in the pipeline.
- **Transformation**: Keep transformations stateless and testable.
- **Feature engineering**: Document the rationale and logic for every feature created from raw data.
- **Storage**: Choose the right storage format (e.g., Parquet for analytical workloads, JSON for flexible nested data).
- **ETL/ELT**: Use clear Extract, Transform, Load (or Extract, Load, Transform) patterns. Prefer ELT when using a modern data warehouse.
- **Batch processing**: Design batch jobs to process partitioned data efficiently (e.g., daily partitions).
- **Streaming concepts**: For streaming, handle out-of-order events and late-arriving data.
- **Data quality**: Implement assertions (e.g., "row count > 0", "column X is never null") in the pipeline.
- **Data lineage**: Track where data comes from and what downstream systems depend on it.
- **Reproducibility**: A pipeline rerun on the same raw data should produce the identical output.
- **Monitoring**: Alert on job failures, data delays (SLA breaches), and data quality anomalies.
- **Failure recovery**: Design pipelines to be restartable from the point of failure without manual cleanup.
