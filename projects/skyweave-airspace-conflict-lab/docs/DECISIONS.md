# Engineering decisions

**ADR-001 — No external GIS dependency.** A regional tangent-plane projection keeps
runtime dependencies light and makes mathematical behavior easy to test. The domain
is intentionally restricted to synthetic regional tracks.

**ADR-002 — Continuous-time windows instead of discrete sampling.** A fixed time step
can miss short conflicts. Quadratic/linear interval solving detects crossings between
samples within the piecewise-linear model.

**ADR-003 — Scenario-level correlated offsets.** Each Monte Carlo trial draws a single
horizontal and vertical error per flight. This is deterministic and avoids introducing
unmotivated high-frequency jitter. It is not a calibrated navigation error model.

**ADR-004 — Content-addressed reports.** Canonical JSON hashing makes repeated runs
idempotent. SQLite audit chaining is useful for a local demonstration but not a substitute
for an external immutable log.
