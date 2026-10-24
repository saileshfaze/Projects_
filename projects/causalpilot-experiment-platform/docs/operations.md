# Operations and failure modes

## Local lifecycle

1. Install Python 3.11+ and `pip install -e '.[api,dev]'`.
2. Run `pytest`, then `python scripts/run_demo.py`.
3. Set `CAUSALPILOT_DB` to a writable file path; avoid `:memory:` because this app opens a new connection per operation.
4. Run the API behind localhost; inspect `/health`.
5. Back up SQLite using its online backup API or a coordinated shutdown; do not copy a live WAL file in isolation.

## Recovery

If an event was rejected for a duplicate subject, inspect whether the event is an accidental replay or whether upstream aggregation is incorrect. The reference system intentionally has no delete/edit endpoint. Backfill and reprocessing should use a new experiment ID or a carefully designed migration, not manual mutation of production data.

## Observability

API access logs and a health endpoint are available through Uvicorn. No Prometheus metrics, distributed traces, alerts, or SLOs are shipped. Suggested production signals: assignment throughput, ingestion error rate, lag to outcome finalization, missing-outcome rate, SRM p-value, and report latency.

## CI

The `ci/github-actions.yml` file is a template only. It must be copied into `.github/workflows/` at repository root to run. Its presence under this project directory does not activate GitHub Actions.
