# Architecture

RouteForge separates **domain rules** from **transport and persistence**. The core modules are pure functions or immutable dataclasses, allowing deterministic tests and reuse from the API or CLI.

```text
JSON / synthetic generator
          |
     parse_problem ----> validation errors
          |
    optimize(problem)
          |----> schedule.evaluate_route (hard feasibility)
          |----> improve.relocate (bounded local search)
          |
     dispatch plan ------> SQLite storage
          |                    |
          |----> Monte Carlo    +--> GET /v1/plans/{id}
          |----> baseline
          +----> SVG / HTML reporting
```

**Request path:** Pydantic enforces basic API collection limits. Domain validation then rejects invalid coordinates, IDs, windows and vehicle parameters. The optimizer constructs candidate insertion moves, rechecks the full route schedule, and records unserved jobs. SQLite uses parameterized SQL and a uniqueness constraint on plan ID.

**Performance:** The insertion heuristic repeatedly evaluates route permutations and is intended for small and medium demonstration workloads. The API caps input at 500 jobs and 100 vehicles but those limits are not performance guarantees. Use a job queue and dedicated VRP solver for large deployments.

**Reproducibility:** Stable job ordering, deterministic tie-breaking and SHA-256 plan IDs support repeatable experiments. Monte Carlo simulations use an explicit seed.
