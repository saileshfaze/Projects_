# Security and privacy model

Aegis is a learning/reference system. Do **not** expose the default configuration to the public internet.

- **Authentication:** optional shared API key via `AEGIS_API_KEY`; constant-time comparison; no per-user identity.
- **Authorization:** not implemented; all authenticated callers can access all feature views. Add tenant isolation and RBAC before multi-tenant use.
- **Secrets:** only placeholders are committed. Never commit `.env`, API keys, cloud tokens, or personal data.
- **Transport:** run behind a TLS-terminating reverse proxy in any remote environment.
- **Data:** example entities and values are synthetic. Real data would require retention, deletion, access logs, consent/legal basis, and privacy review.
- **Abuse resistance:** API batch size is bounded, but no rate limiter or quota system is implemented.
- **Supply chain:** pin and review dependency versions before release; use dependency scanning and container image scanning.
- **Audit:** registration events are logged, but full authenticated actor-level audit is not implemented.

Threats such as feature poisoning, replay abuse, denial of service, and cross-tenant access remain open production engineering tasks.
