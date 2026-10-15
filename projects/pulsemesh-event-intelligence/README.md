# PulseMesh Event Intelligence

A multi-tenant event ingestion and near-real-time analytics reference platform. PulseMesh accepts typed business events, enforces versioned data contracts, deduplicates retries, applies an event-time lateness policy, aggregates sliding time ranges into tumbling windows, and identifies unusual activity with robust statistics.

**Maintainer:** Sailesh ([saileshfaze](https://github.com/saileshfaze)) · **License:** MIT (Copyright (c) 2026 Sailesh)

## Business problem

Product analytics and operational monitoring systems often receive delayed, duplicated, and malformed events. Naive ingestion inflates conversion counts, silently changes event schemas, and creates misleading anomaly alerts. PulseMesh provides a transparent ingestion-to-insight reference architecture that can be run locally without managed cloud services.

## Stack and design

Python 3.12+, FastAPI, Pydantic v2, SQLite (WAL), Prometheus client, pytest, Ruff, Docker, and GitHub Actions CI template. All demo data is synthetic and deterministic. No paid APIs or credentials required.

- **Ingestion:** contract validation, UTC normalization, event IDs unique within a tenant, transactional deduplication.
- **Event-time handling:** a per-tenant high-water mark with configurable allowed lateness; late events are recorded as rejected responses, not inserted.
- **Analytics:** SQL-based tenant-isolated tumbling windows; half-open [start, end) queries; robust median absolute deviation (MAD) anomaly scores.
- **Operations:** health endpoint, low-cardinality Prometheus counters, optional API-key guard, JSONL CLI, schema migration, reproducible SVG architecture asset.
- **Testing:** unit, database, API and CLI tests with isolated temporary databases.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python scripts/migrate.py
python scripts/generate_dataset.py
pulsemesh load data/synthetic_events.jsonl
uvicorn pulsemesh.api:app --reload
```

Windows PowerShell: activate with `.venv\Scripts\Activate.ps1`. Alternatively, `docker compose up --build`.

```bash
curl -s http://localhost:8000/health
curl -s 'http://localhost:8000/v1/tenants/demo/windows?start=2026-10-01T00:00:00Z&end=2026-10-02T00:00:00Z&window_seconds=3600'
curl -s 'http://localhost:8000/v1/tenants/demo/anomalies?start=2026-10-01T00:00:00Z&end=2026-10-02T00:00:00Z&window_seconds=3600'
```

Swagger UI: `/docs`; OpenAPI JSON: `/openapi.json`; metrics: `/metrics`. See [API reference](docs/api.md) and [architecture](docs/architecture.md).

## Development

```bash
python -m pip install -e ".[dev]"
pytest -q
ruff check src tests scripts
python scripts/generate_assets.py
```

The CI workflow under `ci/github-actions.yml` is a **template** for copying to the repository root `.github/workflows/`; GitHub does not execute workflows from nested project folders. Its presence is not evidence that CI ran.

## Limitations

SQLite is a deliberate single-node demonstration choice; this is **not** a distributed stream processor or exactly-once broker. The high-water mark is scoped per tenant, not partition; extreme clock skew and replays require a dedicated backfill process. MAD is an unsupervised heuristic, not a predictive ML model. The optional API key is a minimal demo safeguard, not production IAM. See [security](docs/security.md) and [operations](docs/operations.md).

## Project structure

```text
src/pulsemesh/      API, contracts, storage, analytics, CLI
migrations/         SQLite schema
tests/              domain, persistence, HTTP tests
scripts/            reproducible data/assets and migration
data/               synthetic event examples
assets/             reproducible SVG architecture
docs/               architecture, API, security, operations, ADR
ci/                 GitHub Actions template (not automatically active)
```

All code, sample events, and SVG diagrams in this project are original project artifacts; no third-party media is bundled. Third-party runtime packages retain their respective licenses.
