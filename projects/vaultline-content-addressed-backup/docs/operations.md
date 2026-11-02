# Operator guide

## Installation

Python 3.11+ and optional `pip install -e '.[api,dev]'` for FastAPI/pytest.
For offline use, `PYTHONPATH=src python -m vaultline.cli --help` works without
third-party runtime dependencies.

## Backup and restore drill

1. Generate a fictional corpus with `python scripts/generate_fixture.py ./demo-data`.
2. Run `vaultline --vault ./demo-vault snapshot ./demo-data --label baseline`.
3. Copy the resulting ID; run `verify ID` before any restore.
4. Run `restore ID ./recovered`; compare SHA-256 of each file.
5. Run `audit` to check the SQLite event chain.
6. Preview retention with `prune --keep 3`; add `--apply` only after review.

## Failure handling

- Missing/corrupt objects: `verify` raises an integrity error; do not prune or
  delete the original source until the issue is investigated.
- Corrupt manifest: preserve evidence and restore from a separate backup.
- Concurrent writes: unsupported. Run one Vaultline writer at a time.
- Object orphans after interrupted prune: rerun prune with the same keep count.

The Docker image is an optional API demo. `docker compose up --build` binds
port 8000 to localhost. It has **not** been verified as a hardened deployment.
