# Architecture and data flow

AtlasFlow has four boundaries: ingestion of **metadata**, offline **training**, **promotion policy**, and read-only **inspection**.

1. A dataset is identified by a SHA-256 content digest and row count. Deduplication uses the digest.
2. An experiment is registered with an immutable seed, algorithm name, dataset ID, and JSON configuration.
3. Offline training creates holdout metrics and a local artifact manifest. Evaluation can occur once per run.
4. Promotion checks accuracy, F1, population stability index (PSI), and regression against the current champion.
5. Promotion decisions and their exact policies are stored in an audit table, including failures.
6. Accepted promotion updates the model registry and archives the previous champion within one SQLite write transaction.

The API is intentionally thin: FastAPI -> RegistryService -> Store -> SQLite. The training code is not executed by API requests. This prevents arbitrary remote model execution.

## Consistency

SQLite runs in WAL mode. Each mutation uses BEGIN IMMEDIATE to serialize writers. Registry rows have a unique model name, so at most one champion exists per name. Promotion and audit insertion share a transaction. Idempotency keys prevent duplicate experiment registration after retries.

## Data lineage

Dataset SHA-256 -> dataset ID -> run ID -> model manifest SHA-256 -> promotion audit. Dataset contents and trained weights are not uploaded to the registry; external object storage would be required for multi-host use.

## Drift

PSI uses equal-width bins determined **only from reference data**. PSI is nonnegative; larger values suggest more shift. Thresholds are examples and require calibration for actual datasets. Training/test PSI in the demo is illustrative and is not a substitute for production monitoring.

## Extensibility

- Replace SQLite with PostgreSQL and managed migrations for distributed writers.
- Add S3-compatible artifact storage and server-side digest verification.
- Add OIDC/RBAC, tenant isolation, Prometheus metrics and traces.
- Add queue workers for asynchronous training, shadow validation and rollback policies.
