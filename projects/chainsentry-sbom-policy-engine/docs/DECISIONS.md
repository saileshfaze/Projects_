# Architecture decision records

## ADR-001: Offline-first scanning

**Decision:** all security intelligence is provided through an explicit local feed. **Reason:** deterministic examples, clear provenance boundaries, and no network credentials. **Trade-off:** feed freshness and completeness are entirely external to the engine.

## ADR-002: Canonical normalized inventory hash

**Decision:** hash a sorted JSON representation of the normalized SBOM. **Reason:** a stable identifier across harmless ordering changes. **Trade-off:** a hash proves identity of the normalized representation only; it is not a signature or source attestation.

## ADR-003: Keep exempted findings visible

**Decision:** exemption changes a finding's status, never removes it. **Reason:** reviewers can inspect risk acceptance and expiry. **Trade-off:** reports contain more entries and consumers must interpret the exemption flag.

## ADR-004: SQLite append-only history

**Decision:** keep one report JSON document per scan with an index by project. **Reason:** simple local operation and easy diffing. **Trade-off:** no cross-process concurrency guarantees beyond SQLite's normal locking, no audit integrity proof, and no automatic retention policy.

## ADR-005: Explicit limited standards support

**Decision:** normalize the common fields needed for the demo rather than claiming full CycloneDX/SPDX compliance. **Reason:** the code remains understandable and testable. **Trade-off:** standards-complete validation, SPDX expression evaluation, and ecosystem-specific version logic remain future work.
