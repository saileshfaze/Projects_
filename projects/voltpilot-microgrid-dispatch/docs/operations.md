# Operational guidance

The Docker container runs as non-root UID 10001 and binds the Compose port to loopback. The named volume stores SQLite state. Avoid mounting a production database into the image. `/health` is a liveness endpoint, not a readiness check for persistence. API requests currently run the simulation synchronously; production deployment would need a job queue, quotas, request size limits, authentication and observability.

To inspect a stored run, use `voltpilot list --db state.db` then `voltpilot inspect RUN_ID --db state.db`. The `audit_valid` field recomputes the hash chain. For backup, stop writes before copying the SQLite database, or use SQLite's backup API. Do not rely on the embedded audit chain as a replacement for access controls.
