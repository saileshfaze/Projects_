# ADR 0001 — SQLite snapshots and offline-first scoring

**Status:** Accepted for the reference implementation (2026-10-13).

## Context

A portfolio project should run without paid cloud services, network models or secrets, while still demonstrating versioned contracts and regression analysis.

## Decision

Use SQLite with WAL and immutable snapshot versions; use deterministic token/bigram cosine for default text scoring and optional numeric PSI/KS. Keep an optional local-only sentence-transformer adapter.

## Consequences

Local setup is small and reproducible. Lexical scoring cannot capture paraphrases, and SQLite is not appropriate for distributed high-throughput writes. Production variants should use a dedicated database and evaluated embedding models.
