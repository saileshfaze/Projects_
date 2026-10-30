# Scope and acceptance criteria

The implementation must (1) validate a fictional flight-plan schema, (2) detect
continuous-time conflicts within piecewise-linear segments, (3) return stable results
under flight input reordering, (4) support seeded uncertainty trials, (5) compare
what-if delays, (6) export machine-readable and visual reports, (7) preserve local
runs with verifiable audit hashes, and (8) run tests without external services.

Out of scope: live ADS-B ingestion, aircraft performance modeling, separation
clearances, collision avoidance commands, and regulatory certification.
