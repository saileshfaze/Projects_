# Safety properties and caveats

`check_safety()` checks: at most one active leader per term in the simulated state, contiguous log indices, `last_applied <= commit_index <= last_index`, equality of entries in the committed prefix shared by any pair of nodes, and identical state for nodes at the same applied index. These are runtime assertions, not a model-checking proof.

The leader's commit rule uses a majority and requires the candidate commit entry to belong to the current term. Followers never truncate committed entries; an attempted overwrite is rejected.

**Limitations:** A deterministic seeded scenario explores only its own execution path. Real distributed systems must consider Byzantine behavior, clock skew, torn writes, disk corruption, asynchronous scheduler fairness, network backpressure and membership reconfiguration. This project models none of those. The hash-chain audit detects accidental mutation of a locally stored trace but has no digital signature or external trust anchor.
