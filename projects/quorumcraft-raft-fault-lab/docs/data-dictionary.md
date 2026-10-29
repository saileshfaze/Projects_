# Scenario schema and metric definitions

`data/partition-heal.json`: `schema_version` (integer), `name` (string), `seed` (integer), `nodes` (odd integer >=3), `until` (final logical tick), `actions` (ordered list of `tick`, `kind`, `payload`). Action kinds: `submit`, `partition`, `heal`, `crash`, `recover`.

`data/seed-matrix.csv`: `seed`, `ticks`, `leader_available_fraction`, `leadership_transitions`, `max_committed_index`, `messages_dropped`, `audit_valid`. All results are deterministic simulations, not measured network traffic.

`leader_available_fraction`: fraction of observed ticks with exactly one active leader; it is not a production availability SLO. `leadership_transitions`: number of transitions to a different or newly elected leader in the timeline. `max_committed_index`: highest commit cursor across nodes. `messages_dropped`: transport-level drops from loss, partitions or inactive endpoints.
