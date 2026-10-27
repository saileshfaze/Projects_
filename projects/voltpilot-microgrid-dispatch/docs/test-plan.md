# Test plan

Unit tests cover invalid battery limits, malformed timestamps, energy conservation, SOC constraints, import/export caps, all four strategies, outages, critical-load shedding, deterministic profiles, CSV/JSON roundtrips, idempotent storage, tamper-evident audit chains, CLI operations, report generation and HTTP adapter responses.

The test suite is designed for `pytest -q`. A GitHub Actions workflow template runs compilation, tests and Ruff for changes within this project folder. The workflow is stored inside this project as a template and will not run until copied to the repository root `.github/workflows/`. It has not been assumed to execute merely because the file exists.
