# Security notes

This is a local demonstration, not a hardened public ingestion service.

- Set `PULSEMESH_API_KEY` via a secret manager or environment, never in git. The optional shared key is not scoped to tenants and does not provide authorization isolation.
- Keep the service behind TLS termination and an authenticated gateway before accepting untrusted traffic.
- Limit batch size, payload bytes at the reverse proxy, and request rate. Pydantic limits batch item count, but no network-layer byte/rate limiter is bundled.
- The SQLite query layer uses bound parameters for tenant and time fields. Tenant names are validated by a path pattern.
- Attributes are arbitrary JSON; avoid sending PII or secrets. Logs and metrics intentionally avoid event payloads and tenant labels.
- Rotate keys, audit access, and implement per-tenant permissions before real deployment.
- Dependencies should be scanned and updated; the CI template performs tests/lint but does not claim an audit.
