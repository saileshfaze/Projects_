# Known limitations

- **Not a production compliance system:** no external notarization or independent chain anchoring.
- **No authentication or authorization:** tenant isolation is enforced by query predicates, not caller identity.
- **Single-writer storage:** SQLite serializes writes across tenants. A PostgreSQL implementation would need row/range locking and overlap constraints.
- **Dates, not timestamps, for valid time:** suitable for day-level business facts, not millisecond market data.
- **No deletion/tombstone semantics:** corrections replace facts with payloads; an explicit deletion operation is not modeled.
- **No pagination or bulk ingest transaction:** JSONL loading is sequential and each event is committed independently.
- **No encryption or backup orchestration:** operator responsibility.
- **No formal performance SLA:** the benchmark script is a local reproducible smoke measurement, not a capacity claim.
- **No active CI workflow:** the included file under `ci/` is a template; it must be copied to repository-root `.github/workflows/` to run.
- **No deployment claim:** Docker configuration is provided, but production deployment and container execution are not verified by this repository alone.
