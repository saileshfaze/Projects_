# ADR 0002: SQLite plus hash chain

**Decision:** Use an append-only logical event table with idempotent event IDs and SHA-256 chaining. **Reason:** Low-dependency reproducible local demonstrations and an inspectable audit mechanism. **Tradeoff:** Hash chaining is not a signature and does not survive malicious database rewriting. Real deployments need managed append-only storage, role separation and backups.
