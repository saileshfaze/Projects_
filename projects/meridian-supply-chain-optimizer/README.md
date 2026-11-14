# Meridian — Supply Chain Network Optimization Lab

**Sailesh / [saileshfaze](https://github.com/saileshfaze)** · MIT · 2026

A reproducible, dependency-light integer min-cost flow planner for fictional warehouse-to-store transportation networks. Uses a residual graph and Bellman–Ford successive shortest augmenting paths to find minimum-cost maximum fulfillment with capacity limits. The solver reports unmet demand rather than silently assuming feasibility.

## Quick start

```bash
python -m pip install -e '.[dev]'
pytest -q
meridian data/example.json --output artifacts/plan.json
python scripts/generate.py --seed 2026 --size 8 --output artifacts/generated.json
meridian artifacts/generated.json
```

## Scope and limitations

Integer nonnegative supply/demand/capacity/cost only. Single commodity, linear costs, no lead times, emissions, facility opening, inventory, service levels, stochastic demand, or multi-period constraints. Uses Bellman–Ford for clarity rather than large-scale industrial performance. The demo city names do not represent real routes, costs, or clients. No production deployment is claimed.

See [architecture](docs/architecture.md), [input contract](docs/input-contract.md), and [validation](docs/validation.md).
