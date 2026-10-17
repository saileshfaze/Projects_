# Architecture

The ingestion boundary accepts a versioned JSON Scenario or a CSV of interval measurements. Pydantic validates timestamps, power and tariff fields before a SciPy HiGHS mixed-integer program is constructed. The optimizer returns per-interval power flows and a financial breakdown. A separate invariant checker recomputes power balance and SOC transitions. FastAPI persists successful runs to SQLite with SHA-256 of canonical input JSON. CLI shares the same domain and solver code.

Data flow: CSV/JSON → contracts → optimizer + no-storage baseline → invariant checks → SQLite → API/CLI/report.

**Isolation:** Every request creates a fresh MILP and a unique UUID. SQLite connections are short-lived and WAL is enabled. The prototype does not queue expensive requests or enforce tenant isolation; it is for local analysis.

**Observability:** /healthz exposes liveness. Solver metadata, input digests, and immutable run records aid reproducibility. Production readiness requires tracing, auth, rate limits, backups and worker queues.

**Failure semantics:** Input errors return HTTP 422; infeasible or unproven-optimal solves also return 422 with solver status. Unexpected invariant violations return HTTP 500 and are not persisted.
