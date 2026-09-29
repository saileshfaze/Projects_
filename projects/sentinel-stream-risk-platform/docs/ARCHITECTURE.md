# Architecture

## Request path
1. FastAPI validates the event contract.
2. RiskEngine derives amount/baseline ratio and behavioral features.
3. Isolation Forest contributes an anomaly component.
4. Explicit rules add interpretable risk for velocity, account age and channel.
5. Decision and reason codes are persisted idempotently by transaction ID.
6. Prometheus counters and latency histograms expose service behavior.

## Production evolution
Replace SQLite with PostgreSQL, place Kafka before scoring, maintain an online feature store, package the trained model in an immutable registry, add OpenTelemetry traces, and deploy consumers independently from the API.

## Scaling
Partition the event stream by account_id to preserve customer ordering. API nodes remain stateless except for model memory. Persistence and feature state move to managed stores.
