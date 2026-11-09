# Architecture

A configuration JSON defines variations, ordered targeting rules and integer rollout weights in basis points. Evaluation validates configuration, applies ordered rules, and then hashes `(salt, flag key, subject)` using SHA-256. Buckets are stable in `[0, 9999]`. No network calls or mutable database are needed for evaluation. The experiment module calculates descriptive conversion rates and Wilson intervals from deduplicated subject/variation observations. The JSONL hash chain is a demonstration of accidental-change detection, not cryptographic immutability against an attacker who can rewrite the file.

## Operational limitations

No distributed configuration synchronization, authorization, GDPR consent management, online statistical inference, exposure attribution, or production-grade audit immutability. Changing the salt reassigns cohorts. Rollout weights apply in lexicographic variation order. The example conversion simulation is not causal evidence. Local HTTP API is unauthenticated; bind only to loopback during development.
