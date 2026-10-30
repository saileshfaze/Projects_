# Architecture and module boundaries

`models.py` owns immutable flight-plan dataclasses and validation.
`interpolate.py` performs bounded linear interpolation.
`geometry.py` owns the regional tangent-plane projection and unit constants.
`detector.py` solves separation inequalities for each overlapping segment pair.
`uncertainty.py` runs reproducible Monte Carlo perturbations.
`advisories.py` ranks synthetic departure-delay counterfactuals.
`reporting.py` exports portable, no-network report artifacts.
`persistence.py` implements content-addressed SQLite snapshots and chained audit events.
`service.py` orchestrates analysis. `api.py` and `cli.py` are separate delivery adapters.

The core detector has no dependency on FastAPI, SQLite, or external network services.
All scenario data is fictional and checked into `data/` as reproducible fixtures.
