# Security model

**Deployment classification:** local/demo. This project is not a production authorization service.

## Threats and controls

| Threat | Current control | Remaining work |
|---|---|---|
| Unauthorized writes | Optional constant-time `X-API-Key` check | Enforce secrets and per-tenant RBAC |
| Secrets in repository | Only placeholder `.env.example`; `.env` ignored | Secret manager and rotation |
| SQL injection | Parameterized SQL queries | Database roles and auditing |
| Arbitrary file paths | Fixed SQLite path from environment, no HTTP path control | Container volume policy |
| Resource exhaustion | 1000-sample request cap | Payload byte limit, rate limiting, timeouts |
| Model supply chain | Embedding mode requires a local model directory | Verify model signatures and hashes |
| Data privacy | Synthetic fixtures only | Redaction and retention policy for real payloads |
| Network exposure | Docker port bound to 127.0.0.1 | Reverse proxy TLS, auth and ingress rules |

## Rules

Do not submit real customer payloads without authorization and redaction. Do not expose the default unauthenticated API to the internet. Rotate any compromised keys and rebuild container images after dependency advisories. Dependency versions use compatibility ranges; generate and review a lockfile for a production deployment.
