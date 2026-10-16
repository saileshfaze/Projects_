# Architecture and execution model

Aegis separates **feature definition**, **feature ingestion**, **historical retrieval**, and **online serving**. Its key invariant is that an observation at time T may only read features where both event time and availability time are <= T.

## Data flow

    Feature view (name, version, schema, TTL)
                        |
    Synthetic producer → validated ingestion → immutable feature_events
                                                    |              |
                                           historical join     materialize
                                                    |              |
                                           training rows       online_features
                                                    |              |
                                               ML example       REST GET

See [SVG architecture](../assets/architecture.svg).

## Storage model

SQLite is used for a transparent single-node implementation. `feature_views` stores immutable contracts. `feature_events` is an append-only logical event log keyed by `event_id`. `online_features` is a replaceable materialized snapshot, keyed by (view, version, entity). `materialization_runs` records snapshot executions; `audit_log` records registrations. Foreign keys and an index on historical lookups are created by the bundled SQL migration.

## Temporal correctness

- `event_ts`: timestamp of the real-world event represented by a feature.
- `available_ts`: earliest timestamp at which the value could have been used.
- `ingested_at`: operational time at which this store accepted the event; used for audit, not offline eligibility.
- `as_of`: prediction or label time.
- A valid join requires `event_ts <= as_of`, `available_ts <= as_of`, and `event_ts >= as_of - TTL`.
- Tie-break order is latest event time, then latest availability time, then lexically largest event ID.

For example, an event at 10:00 computed at 15:00 **must not** appear in a 12:00 training observation. The same event becomes eligible for a 16:00 observation if it is still inside TTL.

## Ingestion consistency

Input batches are validated before mutation and committed inside a `BEGIN IMMEDIATE` transaction. Replaying the same `event_id` with identical canonical content increments the duplicate count. Reusing an ID with different content fails and rolls back the entire batch. Feature view versions are immutable.

## Serving semantics

Offline reads query history on demand. Online reads are served from a snapshot built by `materialize`. A snapshot atomically replaces the prior rows for one view version, selecting the latest eligible feature per entity. Online GET refuses expired features, but **does not automatically refresh** the snapshot. Use a scheduler to trigger materialization at the desired cadence.

## Operational scaling path

The prototype intentionally favors auditability over throughput. A production migration could replace SQLite with PostgreSQL, partition event history, use object storage/Parquet for offline features, adopt a stream processor for low-latency online updates, add Redis for online lookup, and integrate OIDC/tenant-aware authorization. Those systems are not represented as already implemented.
