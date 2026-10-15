# ADR-0001: SQLite reference engine and event-time windows

**Status:** Accepted for reference implementation.

## Context

A reproducible portfolio project should demonstrate deduplication, time semantics, and testability without requiring a managed broker or external accounts.

## Decision

Use SQLite WAL with composite primary keys and a tenant high-water mark. Aggregate with SQL into epoch-aligned windows, then score event-type counts using robust MAD.

## Consequences

Low setup cost and deterministic tests. Single-writer contention, no partition-level watermarking, and no built-in horizontal scaling. The repository documents a broker-backed migration path rather than claiming production stream-processing guarantees.
