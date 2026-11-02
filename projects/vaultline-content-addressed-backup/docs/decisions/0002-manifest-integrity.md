# ADR 0002: Canonical manifests and separate audit log

Status: accepted for this lab.

Manifest JSON is serialized with sorted keys and compact separators to produce
stable SHA-256 identifiers. The SQLite audit log independently records actions
with a predecessor digest. Neither mechanism provides signatures or protection
against a privileged writer able to modify the complete store.
