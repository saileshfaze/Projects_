# Operations runbook

## Local startup

1. Install the project with `pip install -e '.[dev]'`.
2. Run `aegis --db data/aegis.db init` to apply idempotent schema setup.
3. Seed demo records with `python scripts/seed_demo.py`.
4. Start the API with `uvicorn aegis_feature_store.api:app --host 127.0.0.1 --port 8000`.
5. Check `GET /ready` and `GET /metrics`.

## Online refresh

Materialization is **explicit**, not automatic. Schedule `aegis materialize VIEW VERSION AS_OF` after each completed ingestion batch. A snapshot built at T cannot contain events that only become available after T. Refresh frequently enough for the business latency requirement.

## Recovery

SQLite WAL mode is enabled for file-backed stores. Before copying the database, stop writers and checkpoint the WAL or use SQLite's online backup API. Restore the database, run `aegis init`, and check counts with `aegis stats`. For a corrupted snapshot, rerun materialization from append-only events.

## Monitoring

Scrape `/metrics` from a trusted network. Track HTTP errors and latency, ingestion duplicate rate, staleness between now and the last snapshot, PSI/KS diagnostics, SQLite disk usage, and batch-processing duration. The service does not yet publish a snapshot-age gauge; add one before production use.

## Known failure modes

- Reused event ID with changed payload → HTTP 409, transaction rollback.
- Naive timestamp → HTTP 422.
- Feature schema mismatch → HTTP 422.
- Expired or absent online feature → HTTP 404.
- Busy SQLite writer → SQLite busy timeout after 15 seconds; retry with jitter in an orchestrator.
- Unexpected data volume → limit batch size and migrate to a distributed store.

## Deployment checklist

Use TLS, strong authentication, tenant-level authorization, network isolation, secrets management, encrypted backups, retention policies, and a managed observability pipeline before handling real customer data.
