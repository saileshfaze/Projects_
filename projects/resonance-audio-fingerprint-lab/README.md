# Resonance Audio Fingerprint Lab

**Offline acoustic fingerprinting, similarity search and interpretable signal diagnostics**  
**Maintainer:** Sailesh (`saileshfaze`) · **License:** MIT (2026)

Resonance is a reproducible Python reference system for ingesting short PCM WAV clips, extracting interpretable acoustic descriptors, indexing spectral landmark pairs in SQLite, and retrieving aligned candidates. It is intentionally self-contained: no external audio catalog, model API, real recordings or secrets are required.

## Why this project

Content matching is a useful example of the boundary between digital signal processing, approximate search, data engineering and API design. This project makes that boundary inspectable: a short-time Fourier transform produces local spectral peaks; time-frequency pairs become stable hash codes; an inverted index returns candidate clips; offset-vote histograms rank candidates.

## Features

- Strict bounded RIFF/WAVE PCM decoder (8/16/24/32-bit integer; mono/stereo downmix).
- STFT, log-mel spectrograms, RMS, zero crossings, spectral centroid/rolloff/flux and silence estimation.
- Landmark pair fingerprinting with deterministic BLAKE2s hashes and 16 kHz canonical resampling.
- Transactional SQLite catalog, SHA-256 exact-file deduplication, cascade deletion, offset-aligned retrieval.
- Local FastAPI service, CLI, batch ingestion, reproducible SVG reports and reproducibly generated synthetic WAV fixtures.
- Unit/integration tests, a deterministic demo, a microbenchmark, Docker Compose and a nested CI template.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python scripts/generate_fixtures.py
python scripts/generate_fixtures.py --check
pytest -q
python scripts/demo.py
resonance --db /tmp/resonance.sqlite ingest data/melody_a.wav
resonance --db /tmp/resonance.sqlite search data/melody_a.wav
resonance analyze data/melody_a.wav --svg /tmp/spectrogram.svg
uvicorn resonance.api:app --host 127.0.0.1 --port 8000
```

Or `docker compose up --build` (binds to loopback port 8000). The API accepts base64-encoded WAV bytes; see `docs/api.md`.

## Architecture

```text
WAV bytes -> bounded decoder -> mono / canonical 16 kHz
                                |                 |
                                v                 v
                           DSP features      STFT peak pairs
                                |                 |
                                v                 v
                          JSON metadata    BLAKE2s landmarks
                                \                 /
                                 SQLite inverted index
                                         |
                              offset-vote candidate ranking
                                         |
                                    REST / CLI
```

## Repository layout

- `src/resonance/`: wave ingestion, DSP, fingerprinting, persistence, API, CLI, reports.
- `data/`: synthetic scenario specification and SHA-256 manifest; WAV fixtures are generated locally.
- `assets/`: generated spectrogram SVG and architecture diagram.
- `scripts/`: generation, demo, validation and microbenchmark.
- `tests/`: deterministic unit, integration and API checks.
- `docs/`: design, assumptions, algorithm, security, testing and operating guidance.
- `ci/project-ci.yml`: example GitHub Actions workflow **not activated** until copied to repository-root `.github/workflows/`.

## Engineering limitations

This is **not** a forensic authentication tool, copyright-enforcement service, speech recognizer, robust music-identification system, or production-scale retrieval engine. It has no learned embeddings and does not prove the origin or ownership of audio. Fingerprints are sensitive to severe compression, pitch/tempo changes and heavy background noise. Scores are uncalibrated alignment votes, not probabilities. Synthetic fixtures and local tests do not establish performance on real audio collections. Raw audio is not stored by the catalog, but fingerprints and metadata may still carry privacy risk.

See `docs/assumptions.md`, `docs/algorithm.md` and `docs/security.md` before adapting the code.
