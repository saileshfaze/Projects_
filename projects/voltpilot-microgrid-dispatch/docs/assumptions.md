# Modeling assumptions and known limitations

1. Load and PV are average AC power over a fixed interval, not instantaneous readings.
2. A single battery and one grid connection are modeled. There is no AC/DC conversion model beyond symmetric charge/discharge efficiency `sqrt(roundtrip_efficiency)`.
3. Grid charging is allowed for price-aware strategy and counts toward the grid import limit.
4. PV is allocated to demand first; surplus may charge the battery or be exported up to the export limit; remaining PV is curtailed.
5. In outages, all available PV and battery output serves demand, with critical demand prioritized. Flexible demand is shed first.
6. During grid availability, battery reserve can be relaxed if the import cap is binding. Reserve is a policy preference, not a hard electrical limit.
7. Price thresholds are 25th and 75th percentile of the provided tariff trace. This is look-ahead using the whole evaluation horizon and is not a deployable forecasting algorithm.
8. Cost includes energy imports, export credits, a simple battery throughput wear term, and a demand charge applied once per horizon.
9. Carbon is grid-import energy multiplied by time-varying illustrative carbon intensity; embodied battery carbon is excluded.
10. Synthetic PV and loads do not represent a real installation. No grid-code compliance, reactive power, transient analysis, battery warranty, thermal limits or real-world validation is claimed.
11. Hash chains are tamper-evident only if their head is stored independently from the attacker.
12. No user authentication, authorization, rate limiting or tenant isolation is implemented in the API.
