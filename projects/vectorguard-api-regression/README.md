# VectorGuard — Semantic API Regression Platform

**Sailesh · [saileshfaze](https://github.com/saileshfaze)**

VectorGuard is a contract-testing service for teams shipping REST APIs. It compares observed JSON response shapes across releases, records immutable baseline versions, and flags regressions before deployment. Alongside schema compatibility it provides offline lexical text drift and optional numeric distribution checks (PSI and two-sample KS distance).

> **Scope:** This is a portfolio reference implementation using synthetic data. It is not a hosted service, and its lexical default must not be confused with neural semantic similarity.

## Why this exists

An endpoint can return HTTP 200 and still break consumers: a required key disappears, a numeric field becomes a string, or customer-facing copy changes unexpectedly. Snapshot testing catches some of these issues but often fails on harmless value changes. VectorGuard compares **inferred structure**, **field presence**, and **drift signals** separately.

## Architecture

```text
Captured JSON samples ──> Schema inference ──> Compatibility rules ──┐
          │                                                          ├─> Evaluation report
          ├───────────────> Lexical token/bigram cosine ─────────────┤   and CI exit gate
          └───────────────> Numeric PSI + KS (optional) ─────────────┘
                                   │
                          FastAPI + SQLite
                     versioned snapshots / audit log
```

## Capabilities

- Sample-driven nested object and array shape inference, required-field intersection, and nullable/type-union handling.
- Backward-compatibility classification: breaking, warning, informational.
- Versioned SQLite baselines with transactional version allocation and append-only evaluation records.
- Numeric population stability index and KS-distance; lexical drift with no model download.
- Optional **local-only** sentence-transformer embeddings for experimentation (not enabled in the default evaluation API).
- FastAPI endpoints with generated OpenAPI docs, API-key guard for writes, CLI gate for CI pipelines.
- Deterministic synthetic fixtures, tests, Docker, GitHub Actions, architecture/operations/security docs.

## Quick start

Requires Python 3.11+.

```bash
cd projects/vectorguard-api-regression
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
uvicorn app.api:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI. In a second terminal:

```bash
curl -X POST http://127.0.0.1:8000/v1/contracts/orders-v1/snapshots \
  -H 'Content-Type: application/json' \
  -d '{"samples":[{"id":1,"total":19.5,"message":"payment accepted"}]}'

curl -X POST http://127.0.0.1:8000/v1/contracts/orders-v1/evaluate \
  -H 'Content-Type: application/json' \
  -d '{"samples":[{"id":2,"total":"19.5","message":"payment denied"}]}'
```

**Offline release gate:**

```bash
python scripts/generate_synthetic.py
vectorguard data/baseline_orders.json data/candidate_orders.json --output reports/evaluation.json
# exit 0 = pass; exit 1 = breaking or drift
```

**Docker:**

```bash
cp .env.example .env
# Set a strong VECTORGUARD_API_KEY before exposing the API.
docker compose up --build
```

The Docker setup binds to localhost by default. Send the configured key in `X-API-Key` for mutating endpoints.

## Repository map

| Path | Purpose |
|---|---|
| `app/schema.py` | JSON response inference and compatibility rules |
| `app/drift.py` | Offline lexical, PSI and KS metrics |
| `app/storage.py` | Versioned SQLite snapshots and evaluation history |
| `app/api.py` | HTTP service and validation |
| `app/cli.py` | Nonzero exit gate for CI |
| `app/migrations/` | Reproducible schema DDL |
| `tests/` | Unit and API integration checks |
| `data/` | Synthetic request/response fixtures |
| `docs/` | API, architecture, threat model, runbook and ADR |
| `scripts/` | Synthetic data and architecture SVG generation |

## Interpreting results

**Breaking:** removed required response fields, required-to-optional changes, or type widening not accepted by the previous shape. **Warning:** removal of a previously optional field. **Info:** additive fields or safe narrowing. A lexical score below the configurable threshold fails the gate even if the schema is compatible. PSI/KS are heuristics, not statistical significance tests; baseline representativeness matters.

## Known limitations

Observational inference cannot prove a contract from a handful of samples. Arrays of mixed types are summarized as unions; nested structural details of unions are intentionally conservative. No distributed locking, rate limiting, RBAC, TLS termination, retention policy or managed migrations are supplied. SQLite is suitable for local/single-node evaluation; production use needs a stronger deployment and security model. See [architecture](docs/architecture.md), [security](docs/security.md) and [operations](docs/operations.md).

## License

MIT License — **Copyright (c) 2026 Sailesh**. Sample data and generated SVG assets are original synthetic materials distributed under the same license.
