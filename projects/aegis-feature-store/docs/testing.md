# Testing strategy

- **Registry:** immutable version registration and version isolation.
- **Ingestion:** duplicate replays, conflicting IDs, atomic validation and timezone enforcement.
- **Temporal correctness:** event-time and availability-time leakage cases, TTL boundaries, and materialization refresh.
- **Quality:** identical distributions, shifted distributions, invalid numerical inputs, and unequal sample sizes.
- **API:** lifespan, optional API key, ingest/join endpoints, and metrics response.

Run locally:

    pip install -e '.[dev]'
    pytest -q
    ruff check src tests scripts examples

The included GitHub Actions file is a **nested template**; GitHub only activates workflows located at repository root `.github/workflows/`. No CI success or deployment is claimed unless a run is actually observed.
