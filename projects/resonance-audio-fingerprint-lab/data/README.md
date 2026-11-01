# Synthetic dataset

The generated WAV fixtures are algorithmically synthesized, not recordings. `scenarios.json` records seeds, durations and signal types. `manifest.json` contains per-file SHA-256 checksums and metadata. Regenerate with `python scripts/generate_fixtures.py` and verify with `--check`.
