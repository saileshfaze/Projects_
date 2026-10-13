# Verification strategy

Unit tests cover schema compatibility, nested arrays, numeric drift, lexical drift, and CLI exit codes. FastAPI integration tests exercise the SQLite snapshot/evaluation lifecycle and API-key validation.

Run `pip install -e '.[dev]' && pytest -q && ruff check app tests` locally. A workflow template is provided at `ci/github-actions.example.yml`; GitHub discovers Actions workflows only under the repository root `.github/workflows/`. This template is not active until installed at that location.

Future work: property-based fuzzing, concurrency tests, and benchmark thresholds.
