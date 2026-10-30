# Test plan

Unit tests cover malformed coordinates, altitude, timestamps, duplicate identifiers,
projection units, interpolation, horizontal quadratic windows, vertical linear windows,
strict boundary behavior, no temporal overlap, segment merging, Monte Carlo seed
reproducibility, advisory ordering, reporting formats, and canonical hashes.

Integration tests exercise FastAPI analysis and run storage, SQLite idempotency and
mutation detection, and the CLI's generated report artifacts. The synthetic fixtures
are intentionally small and are not representative of real traffic density.
