# Operations runbook

## Local setup

Use Python 3.12+, install editable dependencies, initialize schema with `python scripts/migrate.py`, then start the API. To reset local demo data, stop the service and remove the SQLite file and associated WAL/SHM files in `var/` (never do this for production data).

## Dataset replay

Run `python scripts/generate_dataset.py` and `pulsemesh load data/synthetic_events.jsonl --tenant demo`. A second import should report duplicates rather than adding new rows. Synthetic events are dated October 2026; a later event for the same tenant can move the watermark forward and cause older replayed events to be classified late.

## Monitoring

Check `/health` for liveness and `/metrics` for ingestion counts by status. Investigate unexpected growth in late or duplicate counts. Metric counters are per-process and reset on restart.

## Backup and retention

SQLite WAL requires coordinated backup, e.g. Python `sqlite3.Connection.backup`. No automatic TTL or archival is implemented. Define tenant-specific retention and legal requirements before real-world use.

## Failure modes

- `database is locked`: concurrent writes exceeded the SQLite busy timeout; reduce writers or move to a transactional database.
- `422 Unsupported schema_version`: update and review the versioned event contract.
- `late` response: replay using a separate backfill pipeline or adjust lateness policy after assessing ordering guarantees.
- `401`: set the matching `X-API-Key` header when the key is configured.
