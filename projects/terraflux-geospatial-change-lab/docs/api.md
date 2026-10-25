# REST API

Run `uvicorn terraflux.api:app --host 127.0.0.1 --port 8000` after generating a dataset.

- `GET /health` → status.
- `GET /datasets` → registered dataset slugs with both scene files.
- `POST /analyze` → `{ "dataset_id": "demo", "ndvi_drop": 0.20, "nbr_drop": 0.15, "min_patch_pixels": 6 }` → `run_id` and full report.
- `GET /reports` → up to 25 recent run metadata records (`limit` supports 1–100).
- `GET /reports/{run_id}` → persisted report or 404.

The request schema rejects malformed slugs and out-of-range thresholds. Invalid or missing datasets return HTTP 422. Repeating the same analysis returns the same run ID; SQLite does not duplicate the record. There is no authentication, rate limiting, streaming, or asynchronous job scheduler. Bind to localhost for development; place behind an authenticated gateway for controlled use.
