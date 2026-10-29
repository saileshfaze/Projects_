# Security and privacy

No credentials, tokens, real customer records or captured network packets are needed. The example `.env.example` contains only local non-secret settings. The API is intentionally unauthenticated; bind it to loopback and do not expose it to the internet. Docker Compose binds to `127.0.0.1` and uses a read-only container filesystem.

Audit hashes provide local tamper evidence, not cryptographic provenance. A user who can replace both trace and expected hash can forge the entire chain. For real systems use signed checkpoints and trusted external storage.

All datasets are synthetic. Dependency and container security are not independently audited.
