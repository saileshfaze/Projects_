# RouteForge — Logistics Digital Twin

**Author / maintainer:** Sailesh (`saileshfaze`) · **License:** MIT

RouteForge is a Python reference platform for **capacitated vehicle routing with time windows** (CVRPTW). It turns depot, fleet and delivery-order data into feasible dispatch plans, estimates operating cost and transport emissions, and tests how those plans hold up when travel speeds or demand fluctuate.

The focus is practical, reproducible decision support—not an assertion of globally optimal routing or live road-network accuracy.

## What it does

- Assigns prioritized deliveries to heterogeneous vehicles using deterministic cheapest-feasible insertion.
- Checks payload capacity, shift end, latest service start, maximum route distance and return-to-depot constraints.
- Applies bounded inter-vehicle relocation to reduce total cost without dropping already served jobs.
- Returns explicit unserved orders instead of hiding infeasible demand.
- Benchmarks against a transparent first-fit dispatch baseline.
- Runs seeded Monte Carlo stress tests of **fixed** dispatch plans; reports feasibility probability and conditional cost percentiles.
- Stores versionable plan payloads in SQLite with a stable SHA-256-based plan ID.
- Provides FastAPI endpoints, CLI, synthetic CSV/JSON fixtures, SVG route maps and HTML reports.

## Quick start

Requires Python 3.11+.

```bash
python -m pip install -e ".[dev]"
pytest -q
python -m routeforge.cli data/example_problem.json --output artifacts/plan.json
python scripts/generate_report.py data/example_problem.json artifacts/plan.json
uvicorn routeforge.api:app --reload
```

Open the generated `artifacts/report.html` or `artifacts/routes.svg` in a browser.

## API example

```bash
curl -X POST http://localhost:8000/v1/optimize \
  -H 'Content-Type: application/json' \
  --data @data/example_problem.json
```

The API responds with routes, stop ETAs, aggregate cost, emissions, coverage, a first-fit baseline, and a plan identifier. Fetch stored plans using `GET /v1/plans/{plan_id}`. Interactive OpenAPI docs are available at `/docs`.

## Generate reproducible datasets

```bash
python scripts/generate_synthetic.py --count 60 --seed 17 --output artifacts/synthetic.json
python -m routeforge.cli artifacts/synthetic.json --output artifacts/plan.json
python scripts/run_benchmark.py --count 40 --repetitions 3
```

## Container

```bash
docker compose up --build
```

The demo API binds to port 8000. SQLite persists to a named Docker volume. No production authentication is included.

## Project map

`src/routeforge/domain.py` validates the canonical problem schema. `geometry.py` and `schedule.py` compute travel time and feasibility. `optimizer.py` and `improve.py` create and refine plans. `scenario.py` evaluates uncertainty. `storage.py` and `api.py` expose results. `reporting.py` generates static visual reports. `tests/` covers core invariants and API behavior. `docs/` records assumptions and operational considerations.

## Modeling assumptions and limitations

Coordinates use WGS84 degrees. Distances are haversine × **1.35 road-distance factor**; travel time assumes constant vehicle speed. This is a synthetic planning approximation, not turn-by-turn routing. Time windows and shifts are integer minutes after midnight in one local timezone. Demand is a single nonnegative capacity unit; split deliveries, driver breaks, traffic maps, charging stops, and multi-depot operations are not modeled. Cost uses fixed per-vehicle charges plus distance-based variable cost; emissions use a configurable grams/km factor. The heuristic is not an exact solver and does not guarantee optimality or even a maximal served-job count. Stress-test cost percentiles are conditional on feasible trials.

**Validation:** Tests and a CI workflow template are included. GitHub Actions activation and end-to-end deployment are not claimed unless separately verified.

See `docs/architecture.md`, `docs/algorithms.md`, `docs/data_dictionary.md`, `docs/security.md` and `docs/operations.md`.

## License

MIT License — Copyright (c) 2026 Sailesh. The example data and SVG assets are synthetic and created for this project.
