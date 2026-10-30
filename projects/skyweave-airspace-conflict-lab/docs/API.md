# API reference

## `GET /health`
Returns a basic local process health response.

## `POST /v1/analyze`
Accepts `{ "flights": [{"callsign":"SW101", "fixes": [{"t":0,"lat":40,"lon":-74,"alt_ft":30000}, ...]}], "horizontal_nm":5, "vertical_ft":1000, "samples":0, "seed":42 }`.
The `flights` field is required. Each flight requires at least two strictly increasing fixes.
Outputs conflict windows, what-if delay ranking, GeoJSON, and optional risk frequencies.

## `POST /v1/runs`
Same input as analyze; persists a snapshot to SQLite, returns `run_id` and report.

## `GET /v1/runs/{run_id}`
Retrieves a saved report. Returns 404 for unknown IDs.

HTTP 422 is used for invalid request payloads. There is no auth or rate limiting:
this is a local-only development API.
