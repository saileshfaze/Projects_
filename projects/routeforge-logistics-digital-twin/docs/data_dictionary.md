# Input data dictionary

`depot`: `id` (string), `lat` and `lon` (WGS84 decimal degrees).

`jobs[]`: `id` (unique string), `lat`, `lon`, `demand` (positive capacity units), `earliest` and `latest` (integer minutes from midnight, inclusive latest service-start), `service_min` (nonnegative integer, default 5), `priority` (positive integer, default 1).

`vehicles[]`: `id` (unique string), `capacity` (positive capacity units), `shift_start` and `shift_end` (minutes from midnight), `speed_kmh` (positive, default 35), `fixed_cost` (EUR, default 12), `cost_per_km` (EUR/km, default 0.9), `emissions_g_per_km` (grams CO2e/km, default 260), `max_km` (maximum road-adjusted distance, default 300).

Output `routes[]` contains stop arrival/start/departure minutes, distance, load, cost, and emissions. `unserved_job_ids` lists jobs that could not be assigned by the heuristic. `plan_id` is a 16-character prefix of a SHA-256 digest over canonicalized input and route assignments.

All bundled examples are synthetic and do not contain customer information.
