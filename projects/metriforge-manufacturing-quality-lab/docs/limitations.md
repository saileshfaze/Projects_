# Operational limitations and safety

1. No real-world factory validation, instrument calibration, or measurement-system analysis (MSA) was performed.
2. The robust baseline assumes representative, stationary Phase I data. Mixed operating modes invalidate a single control limit.
3. SPC rules overlap and may produce many alerts for one persistent shift; signals are not independent defects.
4. Cp/Cpk and Pp/Ppk are descriptive estimates, not certification of conformance.
5. Lot risk is a transparent heuristic; the label `hold` is a recommendation for **human review**, not an automatic physical stop.
6. The API is intentionally unauthenticated. Bind locally, never expose as a public service.
7. SQLite hash chaining detects accidental edits but does not protect against database rewriting by a privileged actor.
8. The synthetic scenario is intentionally easy to detect and cannot establish real-world false-positive or false-negative rates.
9. The multivariate threshold is in-sample; evaluate on separate data before interpreting as an alarm probability.
10. The project has no claims of deployment, customers, independent industrial testing or professional certification.
