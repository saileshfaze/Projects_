# Reproducibility protocol

1. Use Python 3.11+ in a clean virtual environment.
2. Run `pip install -e '.[dev]'`.
3. Run `python scripts/generate_scenarios.py` and inspect `data/`.
4. Run `python -m pytest -q`.
5. Run `python -m skyweave data/crossing.json --samples 100 --seed 42 --out out --db out/runs.db`.
6. Inspect `out/report.json`, `out/tracks.geojson`, `out/conflicts.csv`, `out/timeline.svg`.
7. Run `python scripts/verify_audit.py out/runs.db`.

The deterministic simulation uses `random.Random(seed)`. No external API, telemetry,
credentials, or paid service is needed. Generated outputs and databases are gitignored.
CI YAML is nested in the project folder and will not auto-run on GitHub unless
explicitly moved to the repository-root `.github/workflows/` directory.
