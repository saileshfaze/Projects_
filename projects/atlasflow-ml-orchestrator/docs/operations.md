# Local operations runbook

## Start and health

    docker compose up --build -d
    curl -f http://127.0.0.1:8000/health
    docker compose logs --tail=100 atlasflow

The named volume atlasflow-data persists SQLite state across container restarts.

## Backup

Stop writes, then use SQLite's online backup API rather than copying a live WAL file:

    python -c "import sqlite3; s=sqlite3.connect('var/atlasflow.sqlite3'); d=sqlite3.connect('backup.sqlite3'); s.backup(d); d.close(); s.close()"

For Docker, run the backup command inside the container and export the result via docker cp.

## Restore

Stop the API, copy the verified backup into the configured database path, ensure the container user owns the file, then restart. Verify /health and a known champion endpoint.

## Migration policy

migrations/001_initial.sql documents the baseline schema, also embedded as package schema.sql for zero-dependency bootstrap. Later schema changes should be additive, numbered, and applied with an explicit migration ledger; the current demo has no automatic upgrade framework.

## Troubleshooting

- HTTP 409: run state transition is invalid, or an idempotency key was reused with different input.
- Promotion accepted=false: inspect /v1/runs/{id}/audit for the exact failed gate.
- Database is locked: reduce concurrent writes, inspect long transactions, or migrate to PostgreSQL.
- Demo training dependency missing: install pip install -e '.[ml]'.
- Drift gate fails: inspect PSI binning and the reference/current distributions before changing thresholds.
