# Threat model and security boundaries

## Assets

SBOM inventory, policy definitions, advisory feed provenance, scan history and local database availability.

## Threats addressed by the reference implementation

- Dangling dependency references are rejected.
- Duplicate component identifiers are rejected.
- Advisory entries with invalid severities or intervals are rejected.
- SQL parameters are bound, not interpolated.
- The Docker image runs as a non-root user, with a read-only root filesystem in Compose.
- No secrets are embedded in sample files.
- Time-bounded policy exceptions retain a justification and remain visible in results.

## Threats not addressed

- **No authentication or authorization:** the API is not suitable for public exposure.
- **No signature/provenance verification:** a malicious SBOM or advisory feed can mislead results.
- **No resource quotas:** extremely large documents or dependency graphs can consume CPU/memory.
- **No complete standards validation:** unsupported SPDX/CycloneDX constructs may be simplified or ignored.
- **No database tamper evidence:** a privileged user can edit SQLite data directly.
- **No authoritative vulnerability intelligence:** the bundled feed is fictional.
- **No exploitability assessment:** reachability means dependency-graph reachability, not runtime exploitability.

## Deployment guidance

For evaluation only, bind the service to loopback, isolate the database, review inputs, and keep dependency packages updated. Production hardening requires authentication, bounded requests, a verified feed supply chain, storage access controls, and security review.
