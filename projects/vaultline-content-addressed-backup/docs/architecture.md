# Architecture and data model

```text
SOURCE DIR -> WALK (skip symlinks) -> GEAR CDC -> SHA256 -> objects/ab/cdef...
                                  |                       |
                                  +--> file hash --> manifests/<sha256>.json
                                                        |
RESTORE TARGET <- safe path <- preflight verify <--------+

snapshot / verify / restore / prune --> audit.sqlite3 (hash-chained events)
```

The snapshot identifier is the SHA-256 hash of canonical JSON *excluding* the
`digest` field. Files are sorted by relative POSIX path, chunks are ordered,
and object paths are split by the first two hex characters. The content-defined
chunker uses a deterministic gear table generated from SHA-256 digests of byte
values, and the cut predicate uses an 8 KiB target mask.

`Vault.prune(keep=N)` retains the N newest manifests and removes objects that
are unreachable from the retained set. Dry-run is the default. A crash between
removing manifests and removing objects can leave harmless orphan objects;
rerun pruning to collect them. SQLite audit entries are not pruned.
