# Operations

Install with `pip install -e '.[dev]'`. Generate synthetic fixtures using `python scripts/generate_fixtures.py`. Start the local service with `uvicorn resonance.api:app --host 127.0.0.1 --port 8000`. For persistent storage set `RESONANCE_DB` to a writable SQLite file. Back up the SQLite file with the standard SQLite backup API or after stopping writers.

`docker compose up --build` creates a named volume and binds the API to loopback. This image is not hardened for public hosting. Inspect resource use before increasing WAV size limits. Avoid logging audio payloads or exposing SQLite files. The CI template in `ci/` must be copied to the repository root to run on GitHub Actions.
