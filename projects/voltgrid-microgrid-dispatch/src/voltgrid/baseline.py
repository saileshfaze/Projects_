"""No-storage counterfactual; import-cap feasibility is reported separately."""

from .domain import Scenario

CURTAIL_PENALTY = 0.0001

def no_storage_baseline(scenario: Scenario) -> dict:
    dt = scenario.interval_minutes / 60
    grid = scenario.grid
    cost = carbon_kg = peak = imported_kwh = exported_kwh = curtailed_kwh = 0.0
    for slot in scenario.slots:
        imp = max(0.0, slot.load_kw - slot.solar_kw)
        exp = min(grid.max_export_kw, max(0.0, slot.solar_kw - slot.load_kw))
        curtail = max(0.0, slot.solar_kw - slot.load_kw - exp)
        imported_kwh += imp * dt
        exported_kwh += exp * dt
        curtailed_kwh += curtail * dt
        carbon_kg += imp * dt * slot.grid_kgco2_per_kwh
        cost += dt * (imp * (slot.import_price_usd_per_kwh
            + grid.carbon_price_usd_per_kg * slot.grid_kgco2_per_kwh)
            - exp * slot.export_price_usd_per_kwh + curtail * CURTAIL_PENALTY)
        peak = max(peak, imp)
    cost += peak * grid.demand_charge_usd_per_kw
    return dict(total_cost_usd=round(cost, 6), carbon_kg=round(carbon_kg, 6),
                peak_import_kw=round(peak, 6), import_kwh=round(imported_kwh, 6),
                export_kwh=round(exported_kwh, 6), curtailed_kwh=round(curtailed_kwh, 6),
                feasible_under_import_cap=peak <= grid.max_import_kw + 1e-8)
