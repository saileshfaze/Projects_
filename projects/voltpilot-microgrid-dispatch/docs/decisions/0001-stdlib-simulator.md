# ADR-0001: Keep simulation core dependency-light

Status: Accepted for the demonstration implementation.

The physical accounting, policy selection, audit and persistence use the Python standard library. FastAPI and Pydantic are only needed for the HTTP adapter. This keeps the core easy to test offline and permits reproducible runs without solver binaries. The trade-off is a heuristic rather than MILP-based optimal dispatch. A later optimizer could implement the same `simulate` contract and be compared against these baselines.
