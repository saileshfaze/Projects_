# ADR 0001 — Deterministic heuristic before exact optimization

**Status:** Accepted for reference implementation.

**Context:** Vehicle routing with time windows is computationally difficult. An exact solver adds dependencies and may obscure the core scheduling constraints in a portfolio demonstration.

**Decision:** Use a cheapest-feasible insertion construction followed by bounded inter-vehicle relocation. Report unserved jobs, hard constraint checks, and baseline comparisons explicitly.

**Consequences:** Results are reproducible, inspectable and easy to test. Optimality is not guaranteed; the heuristic can be suboptimal or fail to assign jobs despite a feasible global solution. A future adapter could integrate OR-Tools or a mixed-integer solver with the same domain contract.
