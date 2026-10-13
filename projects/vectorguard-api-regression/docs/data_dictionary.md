# Synthetic data dictionary

| Field | Type | Description |
|---|---|---|
| id | integer | Synthetic order identifier |
| total | number/string | Synthetic monetary amount; candidate intentionally changes to string |
| message | string | Example status text; candidate intentionally changes copy |
| items | array<object> | Order line examples with SKU and quantity |
| group | string | Baseline/candidate distribution partition |
| latency_ms | number | Synthetic response latency |

Fixtures demonstrate a breaking type change and lexical drift. They do not represent real business traffic.
