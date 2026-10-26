# REST API

The service is intentionally local-only. Start with `uvicorn chainsentry.api:app --host 127.0.0.1 --port 8000` and inspect the OpenAPI document at `/docs`.

## `POST /v1/scans`

Accepts JSON:

```json
{
  "project": "shopfront",
  "sbom": {"bomFormat": "CycloneDX", "components": [{"bom-ref": "app", "name": "app", "version": "1", "purl": "pkg:pypi/app@1"}]},
  "advisories": {"advisories": []},
  "policy": {"fail_at": "high", "deny_licenses": []}
}
```

Returns `{"id": 1, "report": {"status": "pass", ...}}`. HTTP 422 indicates invalid input or policy; the API does not return HTTP errors for a valid policy failure.

## `GET /v1/scans/{id}`

Returns the persisted report and project metadata, or HTTP 404.

## `GET /v1/projects/{project}/history?limit=20`

Returns newest-first scan metadata. Limit is 1..100.

## `GET /v1/diff/{before_id}/{after_id}`

Returns `added`, `resolved` and `changed` findings. The scans must belong to the same project. A missing ID returns 404; different projects return 422.

## Security notes

There is no authentication, tenant isolation, request-size cap, or network advisory synchronization. Use only in a trusted local environment. Do not deploy this API on an internet-facing interface without adding those controls.
