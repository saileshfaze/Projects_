# HydroGraph — Synthetic Water Network Hydraulics

**Sailesh / [saileshfaze](https://github.com/saileshfaze)** · MIT licensed · Engineering portfolio

An offline numerical-engineering laboratory for water-distribution graphs. Implements validated graph models, quadratic pipe head-loss flow, damped Newton nodal-pressure balancing, continuity checks, seeded Monte Carlo demand scenarios, and reproducible JSON/SVG reports. All inputs are fictional.

## Quick start

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
hydrograph --network data/network.json --trials 100 --output artifacts/report.json
python scripts/generate_synthetic.py
python scripts/benchmark.py
```

Optional HTTP: `pip install -e '.[api]' && uvicorn hydrograph.api:create_app --factory --host 127.0.0.1 --port 8000`. `POST /solve` accepts a network JSON; no authentication is provided.

## Architecture

`model.py` validates connected pipe graphs and demand nodes. `solver.py` builds a nonlinear continuity residual and analytic Jacobian and solves Newton steps using pivoted Gaussian elimination with line search. `scenarios.py` applies seeded demand perturbations. `report.py` emits deterministic JSON and a static SVG. See `docs/engineering.md` for equations, assumptions and limitations.

## Reproducibility and provenance

No actual utility maps, telemetry, private data or credentials. All fixtures are generated from source-controlled fictional data. CI is supplied as a nested template and is not activated by committing this folder. Tests are local only unless separately run in CI.

## Safety limitations

**Not for operational water supply, pressure safety, drinking-water decisions, emergency planning or engineering certification.** No pumps, valves, elevation changes, transients, water quality, pressure-dependent demand, pipe aging, leak localization, calibration or real-world validation. Quadratic resistance is an illustrative surrogate; network layout in the SVG is schematic, not geospatial.
