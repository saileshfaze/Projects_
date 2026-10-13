# Operations runbook

Start locally with `uvicorn app.api:app --reload` or run `docker compose up --build -d`. The Compose file binds the API to 127.0.0.1:8000. Set `VECTORGUARD_API_KEY` for any shared deployment.

Check `GET /health` for liveness and `GET /ready` for database readiness. Use `docker compose logs -f api` for logs.

SQLite WAL backups should use the SQLite online backup mechanism (`sqlite3 database.db '.backup backup.db'`) rather than copying a live database file. Test restores before use.

Common errors: 401 means missing API key; 404 means no baseline or evaluation; 422 means invalid payload/metric path; database locks indicate SQLite contention.

CI template is located at `ci/github-actions.example.yml` and must be installed at repository root to become active. There is no production deployment pipeline, distributed storage, or automatic alerting.
