# Testing and reproducibility

Run `python -m pip install -e .` then `python -m pytest -q`. Reproduce synthetic fixtures with `python scripts/generate_fixtures.py` and `python scripts/run_demo.py`. Run `packetforge campaign --seed 2026 --cases 500`. CI workflow is nested under the project and will not run until intentionally copied to repository-root `.github/workflows/`. Do not claim CI or Docker execution unless independently run.

Property tests cover exact round trips, CRC rejection, fragmentation, recovery, bounded lengths, deterministic mutation sequences, and trace metadata validation. No real endpoints are fuzzed.
