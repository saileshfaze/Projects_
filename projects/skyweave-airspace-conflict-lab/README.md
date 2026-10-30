# SkyWeave · Airspace Conflict Lab

**Deterministic, regional-scale aircraft-track conflict analysis with uncertainty experiments.**

SkyWeave is a Python engineering portfolio project by **Sailesh** (`saileshfaze`). It ingests synthetic
flight plans, interpolates piecewise-linear tracks, finds continuous-time intersections of horizontal
and vertical separation constraints, and produces reproducible risk experiments and reports.

> **Simulation only. Never use SkyWeave for real aircraft separation, flight planning, or ATC decisions.**
> No operational aviation data, certified geodesy, regulatory compliance, or safety assurance is provided.

## What is implemented

- Exact interval solving (quadratic horizontal and linear vertical inequalities) per overlapping track segment.
- Flight-pair conflict merging, closest horizontal approach within conflict windows, custom separation thresholds.
- Seeded Gaussian perturbation experiments with per-flight correlated positional offsets and pairwise event frequency.
- Ranked *what-if* departure-delay experiments; these are not flight instructions.
- FastAPI analysis and SQLite run storage with deterministic run IDs and tamper-evident audit records.
- CLI, GeoJSON trajectories, conflict CSV, JSON report, SVG conflict-window timeline.
- Synthetic scenarios, unit/integration tests, Docker/Compose and a nested CI workflow **template**.

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
python scripts/generate_scenarios.py
skyweave data/crossing.json --out out --samples 100 --seed 42
pytest -q
uvicorn skyweave.api:app --reload
```

Open `http://127.0.0.1:8000/docs` for the OpenAPI explorer. Run `docker compose up --build`
to serve the API on localhost port 8080. Docker execution is not required for the local Python tests.

## Example API

```bash
curl -X POST http://127.0.0.1:8000/v1/analyze \
  -H 'Content-Type: application/json' \
  --data @data/crossing.json
```

`POST /v1/runs` stores the scenario and its report, returning a content-derived run ID.
`GET /v1/runs/{run_id}` retrieves it. See [API reference](docs/API.md).

## Architecture

```text
synthetic JSON -> validated flight plans -> piecewise linear interpolation
                                            | 
                                            v
                               continuous-time conflict detector
                                            |
                     +----------------------+------------------+
                     |                      |                  |
               risk sampling          delay experiments     report exporters
                     +----------------------+------------------+
                                            |
                                     REST / CLI / SQLite
```

## Design notes

See [Mathematical model](docs/MATH.md), [Assumptions](docs/LIMITATIONS.md),
[Architecture](docs/ARCHITECTURE.md), [Reproducibility](docs/REPRODUCIBILITY.md),
[Data dictionary](docs/DATA_DICTIONARY.md) and [Security](docs/SECURITY.md).

## License

MIT — Copyright (c) 2026 Sailesh.
