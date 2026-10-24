# REST API reference

Start with `uvicorn causalpilot.api:app --reload` and set `CAUSALPILOT_DB` to a writable path.

## Create experiment

`POST /experiments` with JSON:

```json
{"experiment_id":"checkout-demo","salt":"replace-with-private-long-salt","treatment_fraction":0.5,"alpha":0.05,"planned_looks":1,"minimum_per_arm":20}
```

Reposting the same configuration is safe; a changed configuration is rejected. The salt is stored in the SQLite config JSON. Protect database backups accordingly.

## Assignment

`GET /experiments/checkout-demo/assign/visitor-1` responds with `{"arm":"A"}` or `{"arm":"B"}`. It writes the assignment if not already present. A GET with side effects is an intentional convenience for this demo; production systems should expose a POST allocation endpoint and authenticate callers.

## Ingest outcome

`POST /outcomes`:

```json
{"event_id":"event-1","experiment_id":"checkout-demo","subject_id":"visitor-1","revenue":12.5,"preperiod_revenue":8.0,"converted":true,"refunded":false,"timestamp":"2026-10-01T12:00:00Z"}
```

Returns `{"created":true}` on first ingestion and `{"created":false}` on identical replay. A changed payload with the same ID, or a second outcome for the same subject, returns HTTP 409. Validation failures return 422; unknown experiments return 404.

## Report

`GET /experiments/checkout-demo/report` returns assigned and observed counts, missingness, SRM diagnostic, alpha per planned look, eligibility, pooled CUPED theta, and each metric's arm means, difference and bootstrap interval. Reports include limitations in the `interpretation` field.
