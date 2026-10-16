# Feature contracts and temporal data semantics

Each feature view is identified by immutable `(name, version)`. A definition declares a finite set of lowercase snake_case fields, primitive types, TTL in seconds, and an optional description.

Supported types: `integer` (Python int, excluding bool), `number` (finite int or float), `string`, and `boolean`. Events must supply **exactly** the registered field set. Schema evolution requires a new version.

An event has `event_id`, `entity_key`, `event_ts`, `available_ts`, and `values`. Timestamp strings must include a timezone offset or Z. All timestamps are normalized to UTC with microsecond precision before indexing, avoiding lexical comparison mistakes across time zones.

## Contract evolution

1. Create a new view version with a deliberate field or TTL change.
2. Ingest events for that version; IDs remain globally unique across views and versions.
3. Materialize the new version separately.
4. Change consumers explicitly; no implicit auto-upgrade or cross-version fallback occurs.

## Late-arriving data

`available_ts` expresses when a feature was **actually knowable**, not when it was later replayed into this demo database. A backfill must preserve the original availability timestamp from a trustworthy source. Setting it retroactively to event time would create training leakage.

## Dataset ownership

All committed examples are deterministic synthetic records. No real customer identifiers, credentials, or third-party proprietary datasets are included.
