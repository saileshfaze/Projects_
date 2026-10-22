# Operations runbook

## Development

Install with `pip install -e '.[dev]'`, run `pytest -q`, then start with `uvicorn chronos_ledger.api:app --host 127.0.0.1 --port 8000`. Set `CHRONOS_DB` to an absolute writable path if the working directory may change.

## Container

`docker compose up --build` binds to 127.0.0.1:8000. A named volume persists the SQLite database. The service creates its schema on first access. This does not include an authentication layer or a managed database service.

## Backup

Use the SQLite online backup API rather than copying an actively written WAL database file without coordination. Backups must include the schema, operations and versions. Store copies off-host and periodically rehearse restoration.

## Restore validation

1. Restore to an isolated database path.
2. Run `PRAGMA integrity_check` with the SQLite CLI.
3. Run `chronos-ledger --db restored.sqlite3 audit <tenant>` for every tenant.
4. Check known snapshots against expected values and externally stored chain heads, if available.
5. Only then switch application traffic to the restored file.

## Observability

The demo provides `/healthz` but not production-grade telemetry. Add request latency histograms, write-conflict counts, database lock waits, audit failures and backup-age alarms before deployment.
