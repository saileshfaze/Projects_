# Operations and reproducibility

```bash
pip install -e '.[dev]'
python scripts/architecture.py
python scripts/demo.py
python scripts/check_determinism.py
pytest -q
```

With Docker Compose, `docker compose up --build` starts the API. To create the synthetic dataset in the container: `docker compose exec api terraflux generate --root /app/data/generated --id demo`. Generated data and reports are mounted volumes. This demonstration does not provide a production migration mechanism for SQLite schema changes.

The included `ci/ci.yml` is a template: GitHub Actions only discovers workflows placed at the repository root `.github/workflows/`. Copy it there only after reviewing repository-wide workflow policy. The project folder itself does not activate CI.

For a deterministic experiment, keep the package versions, random seed, input files, thresholds and block-bootstrap configuration fixed. To benchmark performance, run at multiple raster sizes and record memory usage; the current code loads full scenes into memory.
