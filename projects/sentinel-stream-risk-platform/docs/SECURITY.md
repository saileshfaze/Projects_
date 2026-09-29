# Security notes

Assets include transaction events, risk decisions, model artifacts, and service credentials.

- replay/duplicate events: transaction_id idempotency
- malformed payloads: strict validation and numeric bounds
- credential leakage: environment variables; .env excluded
- model evasion: interpretable rules combined with anomaly detection
- data poisoning: training provenance and approval gates in production
- denial of service: add rate limits, queue backpressure, and payload limits
- sensitive logging: never log raw payment credentials

This demo contains synthetic data only.
