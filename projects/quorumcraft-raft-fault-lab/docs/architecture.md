# Architecture and state ownership

The simulation uses a single-threaded logical clock. `Cluster.tick()` increments time, delivers due packets, executes timeouts, applies committed entries, validates invariants and appends a timeline observation. A `Network` instance schedules packets with a stable `(due, sequence)` ordering; the seeded PRNG controls delivery delay and loss.

Each node owns its Raft term, vote, role, log, commit and application cursors, replicated key/value state, request deduplication set, and leader-only `next_index` / `match_index` bookkeeping. There is no shared state-machine object: each node independently applies its committed log.

The transport is an in-memory heap queue, not sockets or threads. Crashes disable message delivery and timers but intentionally preserve in-memory term, vote, log and state for restart. This is an approximation of persistent state, not crash-safe storage.

The CLI and FastAPI adapter share the same cluster engine. Scenario JSON actions are executed at exact simulated ticks. JSON and SVG exports are derived from the simulation and do not influence protocol state.
