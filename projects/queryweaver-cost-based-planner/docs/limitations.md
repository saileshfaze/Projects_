# Limitations and threat model

QueryWeaver is not a production database, optimizer, SQL security gateway, or calibrated benchmark. It accepts a restricted SQL dialect and executes only against fictional in-memory tables. No external database, credentials or real personal data are involved.

The optimizer enumerates left-deep plans only and assumes independent predicates and uniform numeric distributions. Indexed access is modeled rather than physically implemented. LIMIT without ORDER BY is not guaranteed to return the same subset across different join orders. Intermediate materialization may consume memory, so do not expose the demonstration API to untrusted traffic without authentication, quotas and process-level limits.

Local test success does not imply Docker deployment, active CI, or production suitability.
