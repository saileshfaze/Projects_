# Architecture

Chronos is a single-process reference application built around a transactional SQLite store. The API and CLI share the same `Ledger` class, so their write semantics are identical.

## Write path

1. Validate a `Correction` with Pydantic. `valid_from` is inclusive and `valid_to` exclusive.
2. Acquire `BEGIN IMMEDIATE` to serialize writers. SQLite WAL permits readers while a writer is active.
3. Check `(tenant, idempotency_key)` and compare a canonical request hash.
4. Assign a per-tenant monotonically increasing UTC system timestamp.
5. Select current rows whose valid-time intervals overlap the replacement.
6. Close those rows at the new system timestamp; reinsert any unaffected left/right segments.
7. Insert the replacement segment, operation metadata, SHA-256 digests and chain link atomically.
8. Commit or roll back the entire operation.

## Read path

A snapshot selects exactly one row satisfying:

```
valid_from <= valid_at < valid_to
system_from <= known_at < system_to  (or system_to is NULL)
```

A missing match is a 404. More than one match is an integrity failure, not a last-write-wins tie-break.

## Time dimensions

`valid_from`/`valid_to` are ISO dates; `system_from`/`system_to` are timezone-aware UTC ISO timestamps. Lexicographic comparison works because the system normalizes all timestamps to the same offset and precision. Do not bypass the service with ad hoc writes.

## Consistency model

Writes are serializable within one SQLite database file, but there is no distributed coordination. The API is not horizontally scalable for concurrent writes to independent SQLite files. Each tenant has a separate hash chain; tenants share the same database lock.

## Recovery

The database is the source of truth. Use SQLite's backup API, retain backups off-host, and validate integrity and audit chains after restore. An external append-only chain-head archive is needed for adversarial tamper evidence.
