# Synthetic data dictionary

| Field | Type | Meaning |
|---|---|---|
| `event_id` | string | Globally unique synthetic event key; duplicate identical events are replay-safe |
| `timestamp` | ISO-8601 with offset | Simulated observation time, one minute apart |
| `line` | string | Synthetic manufacturing line identifier |
| `machine` | string | Synthetic press identifier |
| `metric` | string | `diameter_mm` |
| `lot` | string | `baseline` or `lot-01` etc. |
| `value` | float | Simulated measured diameter in millimetres |

`labels.csv` provides three binary indicators (`shift`, `drift`, `spike`) describing **injected scenario components**, not human-annotated industrial faults. Seed 2026, 80 baseline readings, 120 production readings, target 50 mm and demonstration specifications [48, 52] mm.
