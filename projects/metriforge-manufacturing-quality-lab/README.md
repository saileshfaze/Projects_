# MetriForge · Manufacturing Quality Lab

**A reproducible industrial quality-monitoring reference system.** MetriForge analyzes dimensional readings from a simulated press line, separates a frozen baseline from production lots, identifies special-cause patterns, computes process capability, and generates audit-friendly reports. Designed and maintained as a software/data portfolio project by **Sailesh (`saileshfaze`)**.

## What is implemented

- **Statistical process control:** Shewhart individual-observation limits, selected Western Electric-style run rules, EWMA with time-dependent control limits, two-sided standardized CUSUM and an offline single-change segmentation diagnostic.
- **Process capability:** Cp/Cpk from moving ranges; Pp/Ppk from overall sample deviation; null values for inadequate samples. Reported alongside the normality and stability assumptions.
- **Multivariate diagnostics:** regularized covariance Mahalanobis scores, with an empirical 99th-percentile training threshold. Correlation ranking is labeled as exploratory, not causal.
- **Lot triage:** transparent heuristic monitor/review/hold suggestions. No automated accept/reject of manufactured products.
- **Data platform:** strict CSV ingestion, immutable event IDs, idempotent replays, SHA-256 hash-chain audit verification, SQLite persistence, JSON and self-contained SVG reporting.
- **Interfaces:** FastAPI app factory, CLI, synthetic scenario generator, reproducible benchmark and tests.

## Quick start

```bash
python -m pip install -e '.[dev]'
python scripts/run_demo.py
pytest -q
uvicorn metriforge.api:app --host 127.0.0.1 --port 8080
```

`run_demo.py` writes to `reports/` and `state/` (ignored). The tracked `data/synthetic/` CSVs are deterministic example data, **not production factory measurements**. All values, equipment identifiers, and lots are fictional.

## CLI

```bash
metriforge generate --out data/generated --seed 2026
metriforge --db state/demo.sqlite load data/synthetic/baseline.csv
metriforge --db state/demo.sqlite load data/synthetic/production.csv
metriforge --db state/demo.sqlite analyze --out reports
metriforge --db state/demo.sqlite audit
```

## Docker

```bash
docker compose up --build
curl http://127.0.0.1:8080/health
```

No real network security, authentication, or production-grade availability is provided. Bind to localhost only. The CI file is **a template inside this project**; GitHub Actions will not execute it until placed in the repository-root `.github/workflows/` directory.

## Structure

| Path | Responsibility |
|---|---|
| `src/metriforge/{rules,ewma,cusum,changepoint}.py` | Interpretable SPC diagnostics |
| `src/metriforge/{stats,multivariate,rootcause,risk}.py` | Capability and exploratory triage |
| `src/metriforge/{store,service,engine}.py` | Persistence, use cases, report aggregation |
| `src/metriforge/{api,cli}.py` | Transport adapters |
| `data/synthetic/` | Seeded demonstration readings and labels |
| `scripts/` | Benchmarks, demos and integrity validation |
| `docs/` | Architecture, statistical assumptions, API and threat model |
| `assets/` | Generated self-contained SVG control chart |

## Limitations

This is **not a certified statistical process control system**, safety controller, validated medical/manufacturing inspection instrument, or a real-time MES integration. Data are synthetic. Correlations do not establish root causes. The demonstration uses retrospective detection and does not claim production sensitivity or specificity. Consult `docs/limitations.md` and `docs/statistics.md` before reusing any method.

**License:** MIT, Copyright (c) 2026 Sailesh.
