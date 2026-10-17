# VoltGrid — Microgrid Dispatch & Carbon Optimization

**Owner:** Sailesh · [saileshfaze](https://github.com/saileshfaze)  
**Status:** engineering reference implementation; not production grid-control software.

VoltGrid helps facility energy analysts compare a solar-plus-battery dispatch plan with a no-storage baseline. It solves a mixed-integer linear program (MILP) for hourly or subhourly power flows, subject to battery state-of-charge, power, grid import/export, and end-of-horizon reserve constraints.

## Business problem

Time-of-use electricity prices, solar variability and demand charges make simple battery schedules expensive. VoltGrid evaluates the trade-off between energy cost, carbon intensity, degradation, solar curtailment and peak demand, while producing an auditable interval-by-interval plan.

## Technology

Python 3.11+, SciPy/HiGHS MILP, NumPy, Pydantic v2, FastAPI, SQLite WAL, pytest, Ruff, Docker, Docker Compose, GitHub Actions CI template, CSV/JSON.

## Quick start

    python -m venv .venv
    source .venv/bin/activate
    pip install -e '.[dev]'
    voltgrid simulate data/demo_scenario.json --db /tmp/voltgrid.sqlite3 --output /tmp/dispatch.json
    pytest
    uvicorn voltgrid.api:app --host 127.0.0.1 --port 8000

Interactive API docs: http://127.0.0.1:8000/docs

    curl -s http://127.0.0.1:8000/healthz
    curl -s -X POST http://127.0.0.1:8000/v1/dispatches \
      -H 'Content-Type: application/json' \
      --data @data/demo_scenario.json

## Repository map

- src/voltgrid/domain.py — strict, unit-aware input contracts.
- src/voltgrid/optimizer.py — mixed-integer battery and grid dispatch.
- src/voltgrid/baseline.py — no-storage counterfactual.
- src/voltgrid/analytics.py — independent physical invariant checks and KPIs.
- src/voltgrid/forecast.py — leakage-safe seasonal naive forecast and empirical error bands.
- src/voltgrid/storage.py — immutable SQLite runs and scenario hashes.
- src/voltgrid/api.py, cli.py — API and command-line interfaces.
- scripts/ — reproducible synthetic scenarios, SVG diagram, PDF report.
- tests/ — domain, solver, API, storage, ingestion and forecasting checks.
- ci/ — CI workflow template (copy to repository-root .github/workflows to activate).
- docs/ — architecture, mathematical model, operations, security, ADR and API details.

## Model behavior

Decision variables per interval are battery charge/discharge, grid import/export, solar curtailment, ending state of charge, and binary battery operating mode; a shared peak-import variable captures demand charges. The objective minimizes USD cost including energy imports, export credits, battery wear, carbon-price penalty and demand charges. The terminal reserve is a minimum, not an equality. The no-storage comparison does not impose the optimized grid-import cap and reports when that cap would be violated.

The input contract forbids export tariffs above import tariffs and validates timestamps, units, ranges and cadence. This is a **planning** tool: there is no live SCADA connection, hardware control, authentication, weather service, external tariff feed or claimed operational deployment. Solver results depend on the quality of input assumptions. A feasible MILP result is not a safety certification.

## Reproducible assets

    python scripts/generate_scenarios.py
    python scripts/generate_architecture.py
    python scripts/generate_pdf_report.py /tmp/dispatch.json /tmp/dispatch.pdf

PDF generation requires pip install -e '.[reports]'. The PDF is generated locally rather than committed; the SVG and synthetic CSV/JSON are tracked.

## Container

    docker compose up --build

The API listens on port 8000 and persists runs to a named Docker volume. Bind the service to localhost for local-only usage; add authentication and TLS before any network deployment.

## License

MIT License — Copyright (c) 2026 Sailesh. All synthetic datasets and the SVG are authored for this repository; no third-party proprietary datasets or media are included. Dependencies retain their own licenses.
