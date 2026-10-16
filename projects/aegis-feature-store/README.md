# Aegis Feature Store

**Point-in-time feature engineering, lineage and serving for machine-learning systems**

Aegis is a reference implementation of a versioned feature store built around one difficult ML engineering requirement: **the feature values used during training must have been available at prediction time**. It provides deterministic historical joins, idempotent ingestion, strict schema contracts, TTL-aware online snapshots, and distribution-shift diagnostics.

**Portfolio owner:** Sailesh (GitHub: saileshfaze)  
**Status:** Runnable engineering reference, not a hosted production service. Synthetic data only.

## Why this project exists

A conventional SQL join can silently introduce target leakage. A transaction may have occurred before a label, but the corresponding feature may only have been computed hours later. Aegis records both `event_ts` (when the underlying event occurred) and `available_ts` (when the feature became available). Historical joins require **both timestamps <= observation time** and enforce the feature view's TTL.

## Architecture

- **Feature registry:** immutable name/version definitions with typed feature contracts.
- **Ingestion:** atomic batches, duplicate-event replay safety and conflict detection.
- **Offline retrieval:** as-of joins over event time **and** availability time.
- **Online serving:** explicit snapshot materialization with expiration checks.
- **Monitoring:** reference-quantile PSI, two-sample KS statistic, Prometheus HTTP metrics.
- **Interfaces:** FastAPI, command-line tools, SQLite schema migrations, optional scikit-learn demo.

See [architecture](docs/architecture.md), [API contract](docs/api.md), [data semantics](docs/data-contracts.md), and [operational runbook](docs/runbook.md).

## Run locally

Requires Python 3.11+.

    cd projects/aegis-feature-store
    python -m venv .venv
    source .venv/bin/activate
    pip install -e '.[dev]'
    aegis --db data/aegis.db init
    python scripts/seed_demo.py
    uvicorn aegis_feature_store.api:app --reload

Open `http://localhost:8000/docs` for interactive API documentation. The default API is unauthenticated **for local development only**. Configure `AEGIS_API_KEY` before exposing a server beyond localhost.

## Example historical lookup

    aegis --db data/aegis.db join customer_risk 1 data/observations.json

The response includes the selected source event ID and values, or null features when nothing was available at the observation timestamp. Try changing the observation time to see late-arriving events excluded.

## Run with Docker

    docker compose up --build

Persistent SQLite data is stored in a named volume. The service is exposed at `localhost:8000`; for shared environments, set `AEGIS_API_KEY`, use TLS via a reverse proxy, and restrict network access.

## Testing and quality

    pip install -e '.[dev]'
    pytest
    ruff check src tests scripts examples

CI workflow **template**: [project workflow](.github/workflows/ci.yml). GitHub recognizes workflows only under the repository-root `.github/workflows/`; this nested template does not run automatically. Activate it at the root only after reviewing repository policy and permissions.

## Reproducible examples

    python scripts/generate_data.py --output data/generated --seed 42
    python scripts/generate_architecture.py
    pip install -e '.[ml]'
    python examples/train_risk_model.py

The optional ML example trains a chronological logistic-regression baseline from synthetic, point-in-time-correct joins. Do not interpret the synthetic evaluation as real-world predictive performance.

## Important limits

SQLite is intentionally chosen for an inspectable single-node prototype, not distributed throughput. Online serving is a manually refreshed snapshot, not streaming synchronization. API-key auth is basic and lacks per-tenant authorization. No external cloud billing or personal data is bundled. PSI thresholds are operational heuristics; monitoring requires human interpretation. See [security and production gaps](docs/security.md).

## Repository layout

    src/aegis_feature_store/   Domain logic, REST API, CLI, bundled migration
    tests/                     Contract, idempotency, leakage, TTL and API tests
    scripts/                   Seed, synthetic data, benchmark, architecture generator
    examples/                  Offline ML training example
    data/                      Small, synthetic JSON samples
    docs/                      Architecture, contracts, API, runbook, ADR, security
    assets/                    Generated SVG architecture diagram
    .github/workflows/         CI template (not active at repository root)

## License

MIT License. Copyright (c) 2026 Sailesh. Synthetic examples and generated SVG assets are created specifically for this project and covered by the same license.
