# HTTP interface

`GET /health` returns `{"status":"ok"}`.

`PUT /specs/diameter_mm` with body:

```json
{"metric":"diameter_mm","lsl":48,"usl":52,"target":50,"unit":"mm"}
```

`POST /readings` with a nonempty array of objects matching the CSV schema:

```json
{"readings":[{"event_id":"demo-001","timestamp":"2026-01-01T00:00:00+00:00","line":"line-07","machine":"press-03","metric":"diameter_mm","lot":"baseline","value":49.95}]}
```

`GET /reports/line-07/press-03/diameter_mm` produces the analytical report if enough baseline and production readings exist. `GET /audit` verifies the hash chain. Invalid specifications and insufficient samples return HTTP 422; conflicting idempotency keys return HTTP 409.

The API intentionally has **no authentication** and should not be exposed to the public Internet. For real use, add TLS termination, authentication, rate limits, tenant isolation and request size enforcement.
