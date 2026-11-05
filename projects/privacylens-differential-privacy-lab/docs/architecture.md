# Architecture

`core.py` contains bounded-contribution filtering, Laplace noise, histogram/mean mechanisms and an in-memory sequential epsilon ledger. `cli.py` exposes deterministic demonstration outputs; `api.py` is optional and explicitly not production-safe. `scripts/` regenerates synthetic CSV and SVG. `tests/` exercises validation, accounting and deterministic mechanisms.
