# HTTP API reference

OpenAPI: `GET /openapi.json`. Interactive docs: `GET /docs`.

All writes require `X-API-Key` **only when** `VECTORGUARD_API_KEY` is set. Configure it for any nonlocal deployment.

## Health

`GET /health` returns `{"status":"ok"}`. `GET /ready` checks SQLite connectivity.

## Register a baseline

`POST /v1/contracts/{contract_id}/snapshots` (201)

```json
{"samples":[{"id":1,"total":19.5,"message":"payment accepted"},{"id":2,"total":20.0,"message":"payment accepted"}]}
```

Contract IDs are lowercase slugs, 3–64 characters, starting with an alphanumeric character. The response contains `contract_id`, monotonically increasing `version`, and inferred `schema`.

## Evaluate a candidate

`POST /v1/contracts/{contract_id}/evaluate` (201)

```json
{
  "version": 1,
  "samples": [{"id":3,"total":25.0,"message":"payment accepted"}],
  "lexical_limit": 0.55,
  "metric_path": "total",
  "psi_limit": 0.2,
  "ks_limit": 0.3
}
```

`version` defaults to the latest snapshot. `metric_path` is optional and supports dot-separated object fields. Missing or nonnumeric values produce 422. The response includes `evaluation_id`, `breaking`, `changes`, `lexical_drift`, optional `metric_drift`, and `verdict`.

## History

- `GET /v1/contracts/{contract_id}/snapshots` — list snapshot versions.
- `GET /v1/evaluations/{evaluation_id}` — retrieve an immutable evaluation record.

## Errors

- 401 — missing/invalid API key when configured.
- 404 — missing baseline or evaluation.
- 422 — malformed slug, samples, thresholds, or metric path.
- 500 — unexpected storage failure; inspect server logs without exposing secrets.

Do not interpret an HTTP 201 as a passing gate; check `verdict` explicitly.
