# Metric definitions

`total_import_kwh`: sum of AC energy imported from the grid, including any battery charging.
`total_export_kwh`: AC energy exported, capped by grid export power.
`total_charge_kwh`: AC energy delivered to the battery charger; stored SOC increases by `charge * sqrt(roundtrip_efficiency)`.
`total_discharge_kwh`: AC energy delivered by the battery inverter; stored SOC decreases by `discharge / sqrt(roundtrip_efficiency)`.
`unserved_kwh`: total load that could not be supplied.
`critical_unserved_kwh`: portion of unserved energy belonging to critical load, after flexible load is shed first.
`emissions_kg`: grid import multiplied by synthetic time-varying grid carbon intensity.
`energy_cost_eur`: import charges minus export credits plus battery wear estimate.
`demand_charge_eur`: highest interval import kW times configured demand-charge rate; applied once per evaluation horizon.
`total_cost_eur`: energy cost plus demand charge.
