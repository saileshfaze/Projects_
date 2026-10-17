# HTTP API

Run locally with: uvicorn voltgrid.api:app --reload

OpenAPI: GET /openapi.json. Swagger UI: GET /docs.

- GET /healthz — liveness.
- POST /v1/dispatches — accepts a Scenario JSON matching data/demo_scenario.json; returns HTTP 201, run_id, schedule, baseline, totals, sustainability and solver metadata.
- GET /v1/dispatches/{run_id} — immutable stored result or HTTP 404.
- POST /v1/forecast — accepts {"history_kw":[1,2,1,2],"horizon":2,"season_length":2,"coverage":0.9} and returns point/lower/upper arrays.

Example: curl -X POST http://127.0.0.1:8000/v1/dispatches -H 'Content-Type: application/json' --data @data/demo_scenario.json

422 means validation failure or no proven feasible optimum; 500 indicates a failed invariant check or unexpected server error. No auth is implemented. Never expose the demo API directly to the public internet.
