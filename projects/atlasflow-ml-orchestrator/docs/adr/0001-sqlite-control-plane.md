# ADR-0001: SQLite for the first control-plane implementation

Status: Accepted for local/reference use

## Context

Experiment metadata and promotion decisions need atomicity, referential integrity, and an audit trail. A portfolio reference implementation should run without cloud accounts or a managed database.

## Decision

Use SQLite in WAL mode with foreign keys, parameterized SQL and BEGIN IMMEDIATE write transactions. Keep model artifacts outside the database and reference them by SHA-256.

## Consequences

Simple setup and reproducible local tests. One writer at a time; no native multi-region support, role-based database authorization, or durable object storage. A future PostgreSQL adapter should preserve the domain-level promotion contract.
