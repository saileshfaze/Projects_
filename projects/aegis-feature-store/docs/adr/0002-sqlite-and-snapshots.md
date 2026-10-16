# ADR 0002: SQLite with explicit online snapshots

**Status:** Accepted for this reference implementation  
**Date:** 2026-10-16

## Context

A small inspectable codebase needs deterministic transactional behavior without requiring cloud infrastructure or background services.

## Decision

Use SQLite with WAL mode, foreign keys, an indexed append-only feature-event table, and an atomic replace-per-view online snapshot. Materialization is an explicit operation.

## Consequences

The design supports portable demos and repeatable tests, but a single SQLite writer limits concurrency. Snapshots can become stale until refreshed. Scaling, high availability, and near-real-time synchronization are intentionally outside this reference implementation.
