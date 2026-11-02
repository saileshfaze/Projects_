# ADR 0001: Deterministic content-defined chunking

Status: accepted for this lab.

Fixed-size blocks shift under small insertions and reduce reuse. Vaultline uses
a deterministic gear rolling hash with configurable min/target/max sizes.
The hash is not cryptographic; SHA-256 addresses the resulting chunks. The
entire source file is currently read into memory. Streaming CDC is a planned
improvement, not an implemented feature.
