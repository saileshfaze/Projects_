# API reference

Base URL: `http://localhost:8000`. Optional `X-API-Key` header is required only when `PULSEMESH_API_KEY` is configured.

## POST /v1/tenants/{tenant}/events

Body:
```json
{
  "events": [
    {
      "event_id": "evt-1001",
      "event_type": "click",
      "occurred_at": "2026-10-01T10:00:00Z",
      "schema_version": 1,
      "value": 1,
      "attributes": {"page": "/pricing", "session_id": "s-12"}
    }
  ]
}
```

Response:
```json
{"tenant":"demo","accepted":1,"duplicates":0,"late":0,"results":[{"event_id":"evt-1001","status":"accepted"}]}
```

Status codes: 200 success; 401 invalid key; 413 batch too large; 422 invalid envelope/contract/time. Duplicate/late events are represented in a 200 response, not as HTTP errors.

## GET /v1/tenants/{tenant}/windows

Required timezone-aware query params: `start`, `end`. Optional `window_seconds` (60–86400, default 3600). Query interval is [start, end); bucket start is UTC-aligned to Unix epoch, so a bucket may begin before `start` when start is not aligned.

Response rows: `bucket_start`, `event_type`, `count`, `total_value`. Only nonempty buckets are returned.

## GET /v1/tenants/{tenant}/anomalies

Same time-range parameters plus optional `threshold` (default 3.5). Response adds `score` and `anomalous`. Scores are computed on counts for each event type across the selected nonempty buckets.

## GET /health and GET /metrics

Health is a process-level probe. Metrics expose Prometheus text format. For full generated API documentation, visit `/docs` or `/openapi.json`.
