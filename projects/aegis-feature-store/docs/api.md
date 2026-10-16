# REST API reference

Base URL: `http://localhost:8000`. Interactive OpenAPI: `/docs`. Machine-readable OpenAPI: `/openapi.json`.

When `AEGIS_API_KEY` is set, provide header `X-API-Key: <value>` for all `/v1` routes. Health and metrics are intentionally unauthenticated and must be protected by network policy in production.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | /health | Liveness |
| GET | /ready | Database readiness and counts |
| GET | /metrics | Prometheus exposition |
| POST | /v1/views | Register immutable feature view |
| GET | /v1/views | List registered views |
| POST | /v1/events:ingest | Validate and ingest event batch |
| POST | /v1/offline:join | Point-in-time join observations |
| POST | /v1/materializations | Refresh online snapshot |
| GET | /v1/online/{view_name}/{entity_key}?version=1 | Read snapshot feature |
| POST | /v1/quality/drift | PSI and KS drift diagnostics |

## Example sequence

    curl -X POST http://localhost:8000/v1/views \
      -H 'Content-Type: application/json' \
      -d '{"name":"account_score","version":1,"ttl_seconds":3600,"fields":{"score":"number"}}'

    curl -X POST http://localhost:8000/v1/events:ingest \
      -H 'Content-Type: application/json' \
      -d '{"view_name":"account_score","version":1,"events":[{"event_id":"e1","entity_key":"a1","event_ts":"2026-01-01T12:00:00Z","available_ts":"2026-01-01T12:10:00Z","values":{"score":0.8}}]}'

    curl -X POST http://localhost:8000/v1/offline:join \
      -H 'Content-Type: application/json' \
      -d '{"view_name":"account_score","version":1,"observations":[{"entity_key":"a1","as_of":"2026-01-01T12:05:00Z"},{"entity_key":"a1","as_of":"2026-01-01T12:15:00Z"}]}'

The first observation has null features (not yet available); the second returns 0.8.

## Error handling

- 401: missing/incorrect API key when auth is configured.
- 404: online feature missing or expired.
- 409: conflicting event ID replay or duplicate view registration.
- 413: batch exceeds configured limit.
- 422: schema/type/temporal validation failure or unknown view.

This is a versioned demonstration API, not a stability guarantee.
