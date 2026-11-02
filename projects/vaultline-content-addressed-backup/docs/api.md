# Optional HTTP API

Start with `VAULTLINE_DIR=./demo-vault uvicorn vaultline.server:app --host 127.0.0.1 --port 8000`.

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Basic status |
| GET | `/snapshots` | List verified manifests |
| GET | `/stats` | Logical and stored bytes |
| POST | `/snapshots` | `{"source":"/absolute/path", "label":"demo"}` |
| GET | `/snapshots/{id}/verify` | Verify object/file integrity |
| POST | `/snapshots/{id}/restore` | `{"target":"/absolute/path", "overwrite":false}` |

The example service has **no authentication**. Do not expose it to untrusted
networks; the POST routes access filesystem paths supplied by the caller.
