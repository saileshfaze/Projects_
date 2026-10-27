# HTTP API

Run `uvicorn voltpilot.api:app` and browse the generated `/docs` OpenAPI UI.

- `GET /health`: liveness probe.
- `POST /simulate`: JSON object with `intervals`, optional `strategy`, `step_minutes`, `battery` overrides, and `site` overrides. Persists a run; returns ID, summary and decisions.
- `POST /compare`: same request shape; returns four strategy summaries.
- `GET /runs`: list persisted runs.
- `GET /runs/{id}`: summary and audit validity, or HTTP 404.

The JSON request in `examples/simulate-request.json` uses four contiguous 15-minute intervals. Values are demonstrative. The service has no authentication; run locally or behind an authenticated gateway.
