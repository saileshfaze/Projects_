# AtlasFlow ML Orchestrator

**Reproducible ML experiments, dataset lineage, drift-aware quality gates, and audited model promotion.**

**Maintainer:** Sailesh ([saileshfaze](https://github.com/saileshfaze)) · **License:** MIT

AtlasFlow is a compact control plane for teams that need to answer: *Which dataset produced this model, what evidence supported its release, and what changed when the champion was replaced?* It provides a transactional SQLite-backed registry, a REST API, deterministic synthetic training data, and a reproducible scikit-learn example. The system separates **experiment metadata** from **model artifact storage** and does not pretend to be a hosted MLOps service.

## Architecture

```text
Synthetic CSV -> SHA-256 dataset registration -> Experiment run
                                              |
                           scikit-learn training + holdout evaluation
                                              |
                        Accuracy / F1 / PSI + artifact manifest hash
                                              |
                  Transactional quality gates and champion comparison
                                              |
                        Registry + append-only promotion audit
                                              |
                            FastAPI / CLI / lineage queries
```

[Architecture](docs/architecture.md) · [API contract](docs/api.md) · [Operations](docs/operations.md) · [Security](docs/security.md)

## Quick start (Python 3.11+)

```bash
cd projects/atlasflow-ml-orchestrator
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,ml]'
python scripts/demo.py --db var/atlasflow.sqlite3
pytest -q
uvicorn atlasflow.api:app --reload
```

The demo generates a **synthetic** customer-retention dataset, trains a logistic regression classifier using a stratified holdout, writes a portable JSON model manifest, and attempts a policy-controlled promotion. No external credentials or data downloads are required.

Open **http://127.0.0.1:8000/docs** for interactive OpenAPI documentation. `GET /health` is a liveness check.

## API workflow

1. `POST /v1/datasets` with a SHA-256 dataset digest and row count.
2. `POST /v1/runs` with model name, dataset ID, algorithm, seed, config, and optional idempotency key.
3. `POST /v1/runs/{id}/evaluate` with holdout accuracy, precision, recall, F1, PSI, and artifact digest.
4. `POST /v1/runs/{id}/promote` with thresholds and a non-regression gate against the current champion.
5. `GET /v1/runs/{id}/lineage` and `GET /v1/runs/{id}/audit` for traceability.

Promotions are serialized using `BEGIN IMMEDIATE`; one champion is stored per model name. Rejected attempts are auditable. An idempotency key cannot silently be reused for a different run payload.

## Repository layout

```text
src/atlasflow/        Domain logic, SQLite store, API, CLI, training
migrations/           Versioned schema baseline
tests/                Unit and API integration tests
scripts/              Reproducible dataset, demo, asset generation
data/                 Small synthetic fixture
assets/               Architecture diagram (SVG)
config/               Example release policy
docs/                 Architecture, API, security, runbook, ADR
.github/workflows/    CI template for relocation to repository root
Dockerfile            Non-root API container
docker-compose.yml    API with persistent named SQLite volume
```

## Engineering decisions and limitations

- **SQLite WAL** keeps local deployment simple; multi-region/high-write throughput needs PostgreSQL and migration management.
- **Content digests** provide lineage references; the server currently trusts submitted hashes rather than uploading or verifying raw artifacts.
- **PSI** is a descriptive distribution-shift signal, not a substitute for model performance monitoring.
- **No authentication** is included. Bind the API to localhost for development; add authn/authz, audit retention, TLS, rate limiting and artifact verification before production exposure.
- **CI template location:** GitHub Actions only executes workflows from the repository root `.github/workflows/`. The nested template documents the intended pipeline but is not automatically active in this monorepo.
- No benchmarks, deployment history, or external clients are claimed.

## License

MIT License. Copyright (c) 2026 Sailesh. All committed datasets and diagrams are synthetic/original; no third-party media assets are bundled.
