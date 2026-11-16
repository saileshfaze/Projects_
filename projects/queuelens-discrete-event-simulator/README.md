# QueueLens — Discrete Event Service Simulator

**Sailesh / [saileshfaze](https://github.com/saileshfaze)** · MIT · Synthetic portfolio engineering lab

QueueLens is a reproducible standard-library-only multi-server FIFO queue simulator. Arrival and service events are modeled with a min-heap, explicit server assignment, optional bounded waiting room, and wait/sojourn/utilization metrics.

## Run

```bash
pip install -e '.[dev]'
pytest -q
python scripts/generate.py --output data/generated.json --seed 2026
queuelens data/example.json --output artifacts/report.json
```

See `docs/architecture.md` and `docs/limitations.md`. Synthetic events are not measured workloads.
