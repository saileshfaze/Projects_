# NimbusLedger — Cloud FinOps Intelligence

**Author:** Sailesh (`saileshfaze`)

Provider-neutral cloud billing ingestion, shared-cost allocation, robust spend anomaly detection and budget forecasting. Synthetic example data only.

## Quick start
```bash
python -m pip install -e '.[dev]'
uvicorn nimbusledger.api:app --reload
pytest
```

## Architecture
`billing CSV → normalization → cost allocation → anomaly scoring → REST API`. See `docs/architecture.md`.

## License
MIT — Copyright (c) 2026 Sailesh.
