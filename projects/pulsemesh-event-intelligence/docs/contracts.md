# Event contracts

The bundled `src/pulsemesh/contracts.json` file defines supported event types and required string attributes. All event envelopes must include a stable `event_id`, timezone-aware `occurred_at`, `event_type`, and optionally `schema_version` (default 1), `value` (default 1), and `attributes` (default empty).

| Type | Version | Required attributes |
| --- | --- | --- |
| click | 1 | page, session_id |
| purchase | 1 | order_id, currency |
| telemetry | 1 | device_id |

New event versions should be added alongside old ones and reviewed for backward compatibility. Unknown types and versions are rejected. This is a required-fields registry, not full JSON Schema validation.
