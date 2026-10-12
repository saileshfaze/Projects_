# Architecture

The API exposes a health endpoint while pure Python domain logic in `app/core.py` implements the core algorithm. Tests validate correctness and edge cases. This is a portfolio reference implementation; production deployment would require authentication, persistent storage, audit logs, metrics, and rate limits.
