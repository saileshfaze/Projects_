# Security review

**Trust boundary:** the API receives a dataset slug, not a path. Slugs are validated against a restrictive regex, and symlinked dataset directories are rejected. NPZ loading disables pickle and enforces exact archive keys. Database queries are parameterized; report IDs are restricted to lowercase hex.

**Residual risks:** locally supplied NPZ files are not considered hostile-input safe: compressed payloads may expand to huge arrays; a malicious file may exhaust memory or CPU. The API has no authentication, tenant isolation, request quotas, TLS termination, or upload endpoint. Docker runs as an unprivileged user, but a production service requires resource limits, authentication, logging, secure image pinning, and dependency scanning.

**Secrets:** `.env.example` contains no credentials. Do not commit `.env`, runtime databases, generated NPZ files, or real geospatial data without permission. Synthetic data contains no personal records.
