# Data dictionary

| Field | Type | Meaning |
|---|---|---|
| `callsign` | string | Synthetic aircraft identifier |
| `t` | float | Seconds relative to scenario start |
| `lat` | float | Decimal degrees north |
| `lon` | float | Decimal degrees east |
| `alt_ft` | float | Synthetic geometric altitude in feet |
| `horizontal_nm` | float | Horizontal conflict threshold, nautical miles |
| `vertical_ft` | float | Vertical conflict threshold, feet |
| `entry_s` / `exit_s` | float | Open conflict interval endpoints, seconds |
| `closest_s` | float | Minimum horizontal separation time within interval |
| `min_horizontal_nm` | float | Minimum horizontal separation in interval |
| `vertical_at_closest_ft` | float | Vertical separation at `closest_s` |
| `pair_probabilities` | map | Fraction of seeded perturbation trials with a conflict |

All bundled records are synthetic. No passenger, flight-tracking, or personal data.
