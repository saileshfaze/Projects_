# Operations runbook

## Development

`python -m pip install -e ".[dev]"`, then `pytest -q`. Use `uvicorn routeforge.api:app --reload` for local API work. The demo CLI is `python -m routeforge.cli data/example_problem.json`.

## Containers

`docker compose up --build`. SQLite is stored at `/app/data/routeforge.db` on the `routeforge-data` volume. Back up the database with SQLite's backup API or by stopping the container and copying the volume. Restore into a stopped container before restarting.

## Troubleshooting

HTTP 422: inspect validation detail for invalid windows, coordinates, demand or vehicle parameters. Unserved jobs: inspect capacity, shift bounds and time windows; the heuristic may also miss feasible global assignments. Slow requests: reduce job count and fleet size, or use a background queue and a dedicated VRP solver.

## Verification

Run unit/API tests, inspect `/health`, submit `data/example_problem.json`, and check that all served routes satisfy capacity and time-window invariants. CI workflow is stored under `ci/workflows/routeforge-ci.yml` as a template; copy it to the repository-root `.github/workflows/` to activate after reviewing permissions.
