# Data dictionary

Scenario: name (string), currency (USD), interval_minutes (15/30/60), slots (2–168 ordered intervals), battery, grid.

Each slot: timestamp (ISO 8601 with timezone), load_kw, solar_kw, import_price_usd_per_kwh, export_price_usd_per_kwh, grid_kgco2_per_kwh. Power is average kW over the interval; multiplying by interval hours gives kWh.

Battery: capacity_kwh, initial_soc_kwh, min_soc_kwh, target_final_soc_kwh, max_charge_kw, max_discharge_kw, charge_efficiency, discharge_efficiency, degradation_usd_per_kwh.

Grid: max_import_kw, max_export_kw, demand_charge_usd_per_kw, carbon_price_usd_per_kg. Demand charge is applied to the maximum modeled import kW over this scenario, not a full billing-month peak.

Synthetic datasets use a fabricated office profile with midday solar, evening load and time-of-use tariffs. They do not represent a real site or actual utility tariffs.
