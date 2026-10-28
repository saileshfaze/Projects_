# Threat model

**Assets:** readings, quality specifications, audit hashes and quality decisions. **Actors:** local developer and an unauthenticated HTTP client. **Trust boundary:** API and CSV input versus local SQLite.

Mitigations: Pydantic validation, finite numeric checks, timezone-required timestamps, event-id conflict detection, parameterized SQL queries, and hash-chain verification. Limitations: no authentication, authorization, TLS, encryption at rest, tamper-proof signatures, payload-size quotas for CLI files, or multi-tenant segregation. Docker binds the service to loopback by default. The SQLite file must be protected by filesystem permissions; `audit` is not a forensic guarantee against a privileged attacker.
