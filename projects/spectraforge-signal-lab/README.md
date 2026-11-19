# SpectraForge — Digital Signal Processing Lab

A reproducible synthetic time-series engineering portfolio project by Sailesh (`saileshfaze`). Implements radix-2 FFT, Hann/rectangular windowing, one-sided amplitude-normalized spectra, spectral peak extraction, seeded signal generation, and past-only rolling anomaly detection. No external dataset or real sensor telemetry is included.

## Quick start

```bash
python -m pip install -e '.[dev]'
pytest -q
spectraforge --samples 256 --rate 256 --seed 42 --output output/report.json --csv output/signal.csv
```

## Architecture

`generate_signal` → `spectrum` (window → FFT → coherent gain normalization) → `dominant_peaks` → JSON/CSV CLI. The anomaly detector is an independent rolling baseline.

## Engineering limitations

The recursive FFT is pedagogical and not optimized for large streams; only powers of two are supported. Peaks are FFT-bin estimates (no sub-bin interpolation), so leakage and finite resolution matter. The detector is sensitive to distribution shifts and is not a validated operational alerting system. Signals are fictional, deterministic and non-clinical.

## Container

`docker compose run --rm spectraforge` writes reports inside the container; mount a host volume if persistence is required. The nested CI template is intentionally inactive until moved into the repository-root `.github/workflows/` directory.

MIT licensed. Copyright (c) 2026 Sailesh.
