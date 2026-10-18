# Security and privacy

This is a local development reference implementation. **Do not expose the API to the public Internet as-is.**

Before production use: add authentication/authorization, tenant isolation, per-user quotas, request timeouts, rate limiting, HTTPS termination, structured audit logs, and encrypted backups. Validate request size at the reverse proxy and cap algorithm execution time. Avoid placing customer addresses or GPS traces in logs, metrics, screenshots or public datasets. Treat location data as potentially personal data under applicable law.

The SQLite connection uses parameterized statements; plan IDs are not authorization tokens. A caller who knows a plan ID could retrieve the plan through the current demo endpoint. Store credentials in a secret manager, not the repository; `.env.example` contains placeholders only.

Dependencies should be pinned and audited in deployment workflows. The example Docker image uses an unprivileged user but is not a substitute for runtime hardening.
