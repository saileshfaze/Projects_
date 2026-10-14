# REST API v1

OpenAPI JSON is served at /openapi.json and Swagger UI at /docs.

| Method | Path | Purpose |
|---|---|---|
| GET | /health | Process health |
| POST | /v1/datasets | Register dataset digest |
| POST | /v1/runs | Register experiment |
| GET | /v1/runs/{id} | Retrieve immutable run metadata and current state |
| POST | /v1/runs/{id}/evaluate | Record holdout metrics exactly once |
| POST | /v1/runs/{id}/promote | Evaluate release gates and record decision |
| GET | /v1/runs/{id}/lineage | Dataset/run lineage |
| GET | /v1/runs/{id}/audit | Ordered promotion audit |
| GET | /v1/models/{name}/champion | Current model champion |

## Example requests

    curl -X POST http://127.0.0.1:8000/v1/datasets \
      -H 'Content-Type: application/json' \
      -d '{"name":"synthetic","sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","row_count":320}'

Use the returned dataset id:

    curl -X POST http://127.0.0.1:8000/v1/runs \
      -H 'Content-Type: application/json' \
      -d '{"dataset_id":"<dataset-id>","model_name":"customer-retention","algorithm":"logistic","seed":42,"idempotency_key":"training-request-001"}'

Evaluation payload:

    {"accuracy":0.91,"precision":0.89,"recall":0.92,"f1":0.90,"drift_psi":0.08}

Promotion policy payload:

    {"min_accuracy":0.75,"min_f1":0.75,"max_drift_psi":0.30,"allow_regression":false}

Errors use {"detail":"..."} with 404 for unknown resources, 409 for invalid transitions, and 422 for invalid schemas. A rejected promotion returns HTTP 200 with accepted=false and machine-readable reasons; this is a **business decision**, not a transport error.
