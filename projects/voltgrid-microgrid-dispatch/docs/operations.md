# Local operations

1. Create a virtual environment and install the package; run pytest.
2. Set VOLTGRID_DB_PATH to a writable path. Use a dedicated SQLite volume in containers.
3. Start with uvicorn voltgrid.api:app --host 127.0.0.1 --port 8000.
4. POST the demo scenario and check /healthz. Review solver status, objective and invariant checks.
5. Back up the database using sqlite3's online backup API or the sqlite3 CLI .backup command; copying a live WAL database file alone can lose data.
6. Tune VOLTGRID_SOLVER_TIMEOUT and VOLTGRID_SOLVER_GAP based on measured workloads.
7. For failed/infeasible scenarios, inspect grid limits, battery terminal reserve and time alignment. Do not silently relax constraints.

Container: docker compose up --build; docker compose down (does not delete named volume). No automatic schema downgrade or production migration manager is supplied.
