# ADR 0002: Do not persist source audio

**Decision:** Persist only SHA-256 payload digests, descriptive features and landmark postings.

**Reasons:** Limit storage cost and avoid retaining raw recordings by default.

**Trade-offs:** Derived fingerprints can still be sensitive; ingestion cannot reconstruct original audio. Exact SHA-256 deduplication is byte-level and does not identify re-encoded duplicates. Retention and access controls remain a deployment responsibility.
