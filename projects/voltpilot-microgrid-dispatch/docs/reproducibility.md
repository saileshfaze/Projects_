# Reproducing results

Python 3.11+ recommended. Run `python -m pip install -e '.[dev]'`, then `pytest -q`.

Generate a deterministic two-day input with `voltpilot generate --days 2 --seed 2026 --out data/demo.json`. Compare policies with `voltpilot compare --input data/demo.json`. Save one run with `voltpilot run --input data/demo.json --strategy price_aware --db state.db --report-dir out`.

The generator uses a local `random.Random(seed)` and a UTC starting date. The output is independent of wall-clock time. SQLite `created_at` records the time of persistence but does not influence the deterministic run ID or summary. No external datasets, APIs, or paid services are required.

The included `data/sample-day.json` is a generated 96-row demonstration trace. See `scripts/benchmark.py` for a machine-readable comparison of strategies and a sample of interval decisions.
