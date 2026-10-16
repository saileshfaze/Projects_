# ADR 0001: Event time and availability time

**Status:** Accepted for this reference implementation  
**Date:** 2026-10-16

## Context

An event can precede a model prediction while its derived feature becomes available only afterward. Joining on event time alone leaks information from the future.

## Decision

Persist `event_ts` and `available_ts` separately, normalize both to UTC, and enforce both <= prediction timestamp during offline joins and online snapshot creation. Preserve the source event ID in returned rows for traceability. Apply TTL relative to event time.

## Consequences

Historical training results are reproducible when source availability timestamps are reliable. Late arrivals remain excluded from earlier labels. The contract places responsibility on upstream pipelines to supply truthful availability timestamps. A source that fabricates historical availability can still create leakage; additional provenance controls would be required in production.
