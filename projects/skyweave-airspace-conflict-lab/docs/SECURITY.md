# Security and operational boundary

This reference API has no authentication. Run only on loopback or behind a properly
configured gateway. Input validation caps the number of flights and fixes to bound
CPU usage, and API Monte Carlo samples are capped at 1000. The local SQLite file
should be protected with normal filesystem permissions. The Docker image runs as
an unprivileged user, and Compose binds to 127.0.0.1 with a read-only root filesystem.

The audit chain provides tamper evidence against casual modifications, not a secure
cryptographic attestation. Never store real flight telemetry or secrets in the repo.
