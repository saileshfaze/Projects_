# HTTP API

Run `quorumcraft serve --host 127.0.0.1 --port 8080`. Interactive OpenAPI docs are served at `/docs`.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Local health check |
| GET | `/cluster` | Node roles, terms, logs, commit cursors and replicated state |
| POST | `/tick` | Advance the logical clock: `{ "steps": 35 }` |
| POST | `/commands` | Submit `{ "request_id": "r1", "op": "put", "key": "x", "value": 5 }` |
| POST | `/faults` | Inject `{ "kind": "crash", "node": "n3" }`, `recover`, `partition` or `heal` |
| GET | `/metrics` | Availability and network counters |
| GET | `/audit` | Hash-chain records and validity |

The command endpoint returns `accepted: true, committed: false` on leader acceptance. Acceptance is **not** a commit acknowledgment; call `/tick` to advance replication and inspect `/cluster` for committed progress. Without a leader it returns HTTP 503. Invalid input returns HTTP 422.

No authentication or authorization is implemented. Do not expose this simulation controller publicly.
