# REST API

Base path: `http://localhost:8000`. FastAPI generates `/openapi.json` and `/docs`.

**GET /health** returns `{"status":"ok","version":"0.1.0"}`.

**POST /v1/optimize** accepts the same JSON structure as `data/example_problem.json`, with optional `include_stress_test: true`. Returns a deterministic `plan_id`, routes and stop schedules, served/unserved job counts, cost, distance, emissions, baseline comparison, and optional Monte Carlo summary. Domain validation errors return HTTP 422. Pydantic caps jobs at 500 and vehicles at 100.

**GET /v1/plans/{plan_id}** retrieves a stored plan or returns HTTP 404.

The API currently has no authentication. API contract stability is not guaranteed in version 0.1.0. JSON output is UTF-8.
