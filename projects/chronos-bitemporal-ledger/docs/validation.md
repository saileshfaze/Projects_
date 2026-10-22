# Local validation record — 2026-10-21

This record describes one local execution environment; it is not a claim about GitHub CI or a production deployment.

- `pytest -q`: **21 passed**.
- `python -m compileall -q src`: **completed without errors**.
- Generated 12 deterministic fictional corrections; initial loader run inserted 12 and the repeated run replayed all 12 without duplicates.
- Tenant audit after loading: **12 operations, 21 historical versions, valid chain**.
- CLI point-in-time query returned a valid synthetic pricing snapshot.
- Local single-process benchmark: 50 synthetic writes, audit valid. Throughput varies by machine and should not be treated as a service-level objective.
- `ruff check`: **not executed** (Ruff not installed in this environment).
- Docker build/runtime: **not executed**.
- Repository-level GitHub Actions: **not activated**; template only.

For independent reproduction, follow the commands in the project README. The benchmark script refuses to overwrite an existing database.
