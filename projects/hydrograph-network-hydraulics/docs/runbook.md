# Runbook

Install Python 3.10+, `python -m pip install -e .`, then run `python -m pytest -q`. Generate alternate fictional demand fixtures with `python scripts/generate_synthetic.py`. Run the CLI from the project root. Inspect `artifacts/report.json` and `artifacts/network.svg`; both are generated, not required for installation.

For a container demo run `docker compose up --build`; the image executes the CLI against the included network fixture and writes output to `/app/artifacts`. The nested workflow under `ci/` is a template; to activate it, explicitly copy it to the repository root `.github/workflows/` after reviewing the project path and permissions.

Security: no secrets required. Do not expose the optional API publicly. Do not treat synthetic heads as validated water pressures.
