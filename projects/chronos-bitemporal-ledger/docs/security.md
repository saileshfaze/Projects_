# Security and threat model

**Do not expose this reference service directly to the internet.** Authentication, authorization, TLS termination, rate limiting, tenant-level access control and audit-log export are not implemented.

## Assets

- Historical business facts and their effective intervals.
- Actor names and idempotency keys.
- Operation chain heads and database backups.

## Controls present

- Parameterized SQL queries; request validation; serialized write transactions.
- No secrets in source files; environment-variable database configuration.
- Non-root Docker user, read-only root filesystem and localhost port binding in Compose.
- SHA-256 checks for payloads, inserted versions, operation metadata and closure consistency.

## Threats not addressed

- A privileged attacker can replace both the database and the in-database chain.
- A malicious API client can write to any tenant because no authorization exists.
- The actor string is caller supplied and not an authenticated identity.
- A compromised host can change wall-clock time or erase backups.
- Payloads are not encrypted at rest by this project.
- Input sizes are not bounded for denial-of-service protection.

## Hardening checklist

Deploy behind an authenticated gateway; bind actor to a verified identity; implement per-tenant authorization; set request-size and rate limits; configure TLS; encrypt storage and backups; export chain heads to an independent append-only service; add backup/restore tests; run dependency and container scans; configure monitoring and alerting.
