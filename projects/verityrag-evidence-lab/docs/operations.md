# Operations and troubleshooting

## Development

Install `pip install -e '.[dev]'`, generate fixtures with `python scripts/generate_data.py`, run `pytest -q` and `ruff check src tests scripts`. Launch `uvicorn verityrag.api:app --reload` for a local API. Use `VERITYRAG_DB` to select the SQLite file.

## Data management

`verityrag --db ./demo.db ingest data/documents.jsonl` upserts by ID. Upserts replace previous content rather than keeping document revisions. `evaluations` records contain a corpus SHA-256 fingerprint and JSON metrics; they do not snapshot the original corpus. Back up the SQLite file while no writer is active or use SQLite's backup API.

## Troubleshooting

- Empty search results: confirm ingestion and verify token overlap; this baseline is lexical.
- Abstentions: inspect query terms and document filtering; lower the overlap threshold only after evaluation.
- Locked database: avoid concurrent writes; move to a transactional server database for multi-worker use.
- Unexpected performance: rebuilding the index for each API request is O(corpus size); batch evaluations and cache indexes for larger workloads.

## CI

The template at `ci/project-ci.yml` is not active while stored in this project directory. Copy it to `.github/workflows/verityrag.yml` at the repository root only when you are ready to enable GitHub Actions. That action changes repository-level configuration.
