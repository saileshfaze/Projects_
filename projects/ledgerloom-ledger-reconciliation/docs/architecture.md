# Architecture

`Journal` persists immutable postings and canonical JSON audit events to SQLite. Each event includes a SHA-256 digest over its predecessor digest and canonical payload. `reconcile` reads statement rows and compares against account ledger entries without mutating either. CLI/scripts provide deterministic local workflows; the optional API exposes read-only status. All monetary amounts are integer cents. The demo creates a fresh temporary database.
