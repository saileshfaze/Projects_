# Security model and threat boundaries

**Deployment scope:** local development and demonstration. The API is unauthenticated. Docker Compose binds to 127.0.0.1 by default. Do not expose this service publicly without an authenticated reverse proxy and request throttling.

- No secrets or real customer records are included. Data and diagrams are synthetic.
- Use ATLAS_DB_PATH to select a writable location. Avoid network-mounted SQLite volumes.
- The server accepts client-submitted digests. It does **not** verify remote model artifacts or datasets; add signed manifests and server-side verification for production.
- Do not load untrusted pickle/joblib artifacts. The demo writes JSON metadata, not executable serialized objects.
- Idempotency keys must be unpredictable if used as correlation identifiers, not authorization tokens.
- SQLite parameterized queries are used for user-supplied values. Model names are validated.
- Pydantic rejects non-finite evaluation metrics and out-of-range scores.
- Backups and audit logs may contain sensitive metadata in real deployments; apply retention and encryption policies.

Production checklist: OIDC, RBAC, TLS, tenant isolation, structured logging, request IDs, rate limiting, database backup/restore exercises, schema migration tooling, artifact integrity checks, and supply-chain scanning.
