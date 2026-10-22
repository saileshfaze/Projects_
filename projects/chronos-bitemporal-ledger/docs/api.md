# REST API

Interactive OpenAPI documentation is available at `/docs` when the service is running.

| Method | Endpoint | Behavior |
| --- | --- | --- |
| GET | `/healthz` | Basic process liveness |
| POST | `/v1/tenants/{tenant}/entities/{entity}/corrections` | Write a valid-time correction |
| GET | `/v1/tenants/{tenant}/entities/{entity}?valid_at=YYYY-MM-DD&known_at=...` | Bitemporal snapshot |
| GET | `/v1/tenants/{tenant}/entities/{entity}/history` | All versions, including superseded rows |
| GET | `/v1/tenants/{tenant}/audit` | Integrity report |

## Correction request

```json
{
  "valid_from": "2026-01-01",
  "valid_to": "2027-01-01",
  "payload": {"monthly_eur": 49, "currency": "EUR"},
  "actor": "demo",
  "idempotency_key": "acme-plan-1-v1"
}
```

The response includes `operation_id`, `recorded_at`, `chain_hash` and `replayed`. Repeated requests with an identical key and content return the original receipt (`replayed: true`). A changed request with a reused key returns 409.

## Errors

- 404: no version at the requested valid and system times.
- 409: idempotency-key conflict.
- 422: malformed date, invalid interval or other validation error.
- 500: unexpected storage or invariant failure. Do not expose raw stack traces in production.

No pagination, authentication, rate limiting or tenancy authorization is included in the reference API. Avoid publishing it to the public internet.
