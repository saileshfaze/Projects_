# Architecture and data flow

## Boundary

ChainSentry accepts an SBOM JSON document, a separate advisory JSON document, and a policy JSON document. All inputs are treated as untrusted. The analysis core has no network dependency and no database dependency. The API and CLI are thin adapters around `service.scan()`.

## Pipeline

1. **Parse:** select CycloneDX by `bomFormat` or SPDX by `spdxVersion`, normalize to immutable `Component` records and dependency adjacency lists. Reject duplicate identifiers and unknown dependency references.
2. **Graph:** infer roots if none are explicitly supplied; traverse with BFS and retain shortest deterministic paths. SCC diagnostics use Tarjan's algorithm and handle cycles.
3. **Advisories:** load a local feed and compare normalized PURL package names plus `introduced <= version < fixed`. `fixed=null` means no upper bound. The interval is not a complete version range language.
4. **Policy:** produce findings for matched advisories, denied license identifiers, and optionally missing metadata. Apply time-bounded exemptions while retaining the finding. Decide pass/fail using severity threshold and reachability.
5. **Evidence:** hash the canonical normalized inventory with SHA-256, serialize findings deterministically, and optionally append a scan to SQLite.
6. **Drift:** compare two persisted reports by `(kind, rule, component, advisory)` and show added, resolved, and changed findings.

## Invariants

- A normalized graph cannot contain dangling edges.
- A scan cannot silently mutate the caller's SBOM, feed, or policy.
- A policy exemption does not remove a finding.
- Input ordering does not affect the normalized inventory digest.
- Drift comparisons do not require external services.

## Storage schema

`scans(id, project, created_at, digest, status, report_json)` with an index on `(project, id)`. SQLite transaction boundaries are per scan insertion. Scan history is append-only through the application API, not tamper-evident against database administrators.

## Operational constraints

The reference API performs synchronous CPU-bound evaluation and writes to SQLite. For large SBOMs, add payload-size limits, bounded parsing, a task queue, and concurrency controls. A public service requires authentication, authorization, auditing, abuse protection and separate storage per tenant.
