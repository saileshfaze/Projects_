# Design decisions

## Why bitemporal instead of an `updated_at` column?

Backdated corrections change what is *currently believed* about the past. Without two time dimensions, the previous belief is lost. Separating valid time and system time makes regulatory and incident reconstruction queries possible.

## Why split intervals?

Replacing only a subrange must not change the rest of an entity's effective history. Splitting and reinserting untouched fragments preserves the exact current valid-time coverage. This deliberately favors auditability over compact storage.

## Why SQLite?

SQLite is a reproducible, dependency-light reference store with ACID transactions. `BEGIN IMMEDIATE` serializes conflicting writes, making interval updates and idempotency checks atomic. Production-scale write throughput and horizontal scaling would require a different storage architecture.

## Why not coalesce adjacent equal payloads?

Adjacent segments can originate from different corrections. Coalescing would obscure operation provenance. An explicit compaction process could be added later with a documented lineage mapping.

## Why SHA-256 digests?

Digests detect accidental corruption and some unauthorized modifications. They are not signatures. The chain head is stored alongside the data and can be rewritten by a sufficiently privileged adversary. External anchoring is out of scope.

## Why one key per tenant?

Tenant-scoped idempotency makes retries deterministic across entities within a tenant. Reusing a key for a different entity is treated as a conflict, not as a separate request.
