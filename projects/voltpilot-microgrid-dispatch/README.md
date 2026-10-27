# VoltPilot — Microgrid Dispatch Lab

**An auditable, offline microgrid simulator for battery, rooftop solar, grid tariffs and resilience trade-offs.**

VoltPilot compares four explicit dispatch policies on the same quarter-hourly synthetic demand and PV trace. It calculates AC-side energy balance per interval, models battery round-trip losses, enforces inverter and grid caps, and produces an immutable SQLite run with a SHA-256 interval audit chain. The system has a Python library, CLI, FastAPI service, Docker Compose, and self-contained SVG reporting.

## Quick start

```bash
python -m pip install -e '.[dev]'
voltpilot generate --days 2 --seed 2026 --out data/demo.json
voltpilot compare --input data/demo.json
voltpilot run --input data/demo.json --strategy price_aware --db state.db --report-dir out
pytest -q
```

Run the API using `uvicorn voltpilot.api:app --reload`; browse `/docs`. `docker compose up --build` starts the API at `http://127.0.0.1:8000`. A sample POST request is in `examples/simulate-request.json`.

## Policies

| Policy | Battery decision |
|---|---|
| `baseline` | No voluntary battery cycling; emergency discharge if import cap is binding |
| `self_consumption` | Charge with excess PV, discharge to cover demand |
| `price_aware` | Charge from grid below 25th-percentile price, discharge above 75th; charge from excess PV |
| `resilience` | Preserve configurable reserve during grid availability; use reserve in outages |

All policies respect `min_soc`, `max_soc`, power limits and AC-side conservation. Unserved energy and critical-load unserved energy are tracked during outages or grid import constraints. Battery wear is a simplified per-throughput cost, not a calibrated electrochemical aging model.

## Project map

- `src/voltpilot/dispatch.py`: physically constrained, deterministic interval simulator
- `src/voltpilot/models.py`: domain validation and result contracts
- `src/voltpilot/synthetic.py`: deterministic illustrative load/PV/tariff/carbon traces
- `src/voltpilot/storage.py` and `audit.py`: SQLite idempotent run records and hash verification
- `src/voltpilot/report.py`: Markdown and SVG report generation
- `src/voltpilot/api.py` and `cli.py`: HTTP and command-line adapters
- `tests/`: accounting, constraints, outage, audit, persistence, API, CLI tests
- `docs/`: design, API, assumptions, reproducibility, operational notes

## Inputs and units

Every row has timezone-aware ISO timestamp, load/PV in **kW**, import/export prices in **EUR/kWh**, carbon intensity in **kg CO₂/kWh**, and a grid-availability flag. Power is converted to interval energy using `step_minutes / 60`. SOC is in kWh. All money values are EUR. Demand charges are optional and applied to the maximum interval-average import power, once per simulated profile (not prorated).

## Security and limitations

No secrets or measured customer data are included. The input dataset is synthetic, with fixed seed. The simulator is **not** an electrical engineering design tool, a certified controller, a power-flow solver, a dispatch guarantee, or a market-price forecast. It omits reactive power, thermal derating, degradation curves, multi-phase constraints, network losses, utility tariff minimums, uncertainty optimization, and protection-system engineering. The price-aware heuristic is not globally optimal. The API has no authentication and should not be exposed publicly without a gateway. The nested `.github/workflows/ci.yml` is a **template**: copy it to the repository root `.github/workflows/` to activate GitHub Actions. See `docs/assumptions.md`.

Maintainer: Sailesh (`saileshfaze`). License: MIT, Copyright (c) 2026 Sailesh.
