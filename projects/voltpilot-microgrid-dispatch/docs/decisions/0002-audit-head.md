# ADR-0002: Hash chain each interval

Status: Accepted.

Each interval is encoded as canonical JSON, hashed with the previous SHA-256 digest, and stored with its index. This makes modifications visible during audit verification. The chain is not signed; an adversary who controls the database can recompute it. A production version would anchor the head digest to a separate trust domain.
