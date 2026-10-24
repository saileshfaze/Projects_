# Threat model and privacy limits

- **Authentication:** Not implemented. The API must not be publicly exposed as-is. Add authentication, authorization, request limits, and TLS at an ingress layer before any deployment.
- **Identifiers:** Subject IDs are not anonymized; synthetic IDs only are included. Production use requires pseudonymization, deletion policy, and regional privacy-law review.
- **Salt secrecy:** Experiment salts are stored in the database and supplied through the registration API. Never reuse demo salts with real users. Store secrets in a secret manager and avoid request logging.
- **SQL injection:** SQL statements use positional parameters; identifiers are validated to a narrow ASCII set.
- **Integrity:** Event IDs and unique experiment/subject pairs block duplicate counting, but the database has no tamper-evident audit chain.
- **Resource exhaustion:** No request rate limits or row caps are enforced. Bootstrap processing is O(draws × subjects) and is vulnerable to expensive report requests.
- **Network:** Compose binds localhost only. Docker runs as a non-root user. No penetration test has been performed.
