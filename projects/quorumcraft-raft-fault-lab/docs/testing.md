# Test strategy

Run `python -m pytest -q` after `pip install -e '.[dev]'`. The suite includes protocol elections, command semantics, follower catch-up, crash/recovery, majority isolation, network delay/loss, reproducible scenarios, invariant failure detection, audit tampering, FastAPI request validation, CLI exports and deterministic stress seeds.

For a broader but still bounded exploration, run `python scripts/stress_matrix.py --seeds 100`. It varies the seed while injecting repeated writes, a partition, a crash and recovery. Each simulated tick checks safety invariants. This is a randomized regression harness, not a formal model checker or a distributed deployment test.

Python compilation: `python -m compileall -q src scripts tests`. Ruff template: `ruff check src tests scripts` (requires optional development dependency). Docker template: `docker compose up --build` (requires a Docker daemon). The CI YAML lives inside this project and is not automatically executed by GitHub Actions.
