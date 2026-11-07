# SeismoScope — Synthetic Seismic Event Lab

**Sailesh / [saileshfaze](https://github.com/saileshfaze)** · MIT licensed · Engineering portfolio

SeismoScope is a deterministic, self-contained seismic waveform laboratory. It generates five fictional seismic station traces, detects abrupt energy changes with short-term/long-term average ratios, associates picks across stations, and estimates a 2-D epicenter and origin time by travel-time grid search.

## Quick start

```bash
python -m pip install -e .
seismoscope --seed 42 --output artifacts/report.json
python scripts/generate_fixtures.py
python scripts/generate_svg.py
python -m pytest -q
```

Optional HTTP API: `pip install -e '.[api]'` and `uvicorn seismoscope.api:create_app --factory --reload`. Endpoints: `GET /health`, `GET /simulate?seed=42`.

## Architecture

`synthetic.py` → deterministic noisy traces → `signal.py` STA/LTA picks → `associate.py` temporal coincidences → `locate.py` bounded grid search → `pipeline.py` JSON report. Python standard library implements the numerical routines; optional FastAPI is isolated from the core. See `docs/architecture.md` and `docs/limitations.md`.

## Data and provenance

All stations, coordinates, waveforms, and event times are fictional. The generated JSON assets are reproducible from seed 42; no real-world data or secrets are included. The CI workflow is a **nested template**, not automatically active on GitHub.

## Limitations

Not for earthquake warning, public safety, seismic hazard assessment, or scientific inference. No calibration, instrument response, 3-D velocity models, depth estimation, phase identification, uncertainty quantification, real-time ingest, or independent validation. A constant wave speed and grid resolution produce model-dependent estimates; association is deliberately simplistic. No performance claims are made beyond explicitly executed local tests.
