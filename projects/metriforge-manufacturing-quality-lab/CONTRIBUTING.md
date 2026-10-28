# Development

Install with `python -m pip install -e '.[dev]'`, run `pytest -q`, regenerate deterministic fixtures with `python scripts/generate_data.py`, and run the local demo with `python scripts/run_demo.py`. Do not commit secrets or production factory data. Add a regression test for each defect fix, keep control limits reproducible, and document any statistical assumption changes.
