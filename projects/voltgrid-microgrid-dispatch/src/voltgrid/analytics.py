"""Independent dispatch invariant checks and sustainability indicators."""

from .domain import Scenario

def validate_solution(scenario: Scenario, result: dict, tolerance: float = 2e-4) -> list[str]:
    issues = []
    dt = scenario.interval_minutes / 60
    battery = scenario.battery
    previous_soc = battery.initial_soc_kwh
    if len(result["schedule"]) != len(scenario.slots):
        return ["schedule length differs from input"]
    for i, (slot, row) in enumerate(zip(scenario.slots, result["schedule"])):
        lhs = (row["grid_import_kw"] - row["grid_export_kw"] - row["charge_kw"]
               + row["discharge_kw"] - row["solar_curtail_kw"])
        if abs(lhs - (slot.load_kw - slot.solar_kw)) > tolerance:
            issues.append(f"slot {i}: power balance")
        soc = (previous_soc + dt * battery.charge_efficiency * row["charge_kw"]
               - dt * row["discharge_kw"] / battery.discharge_efficiency)
        if abs(soc - row["soc_kwh"]) > tolerance:
            issues.append(f"slot {i}: SOC transition")
        if row["charge_kw"] > tolerance and row["discharge_kw"] > tolerance:
            issues.append(f"slot {i}: simultaneous battery charge and discharge")
        if row["grid_import_kw"] > scenario.grid.max_import_kw + tolerance:
            issues.append(f"slot {i}: grid import capacity")
        if row["solar_curtail_kw"] > slot.solar_kw + tolerance:
            issues.append(f"slot {i}: solar curtailment exceeds generation")
        previous_soc = row["soc_kwh"]
    if previous_soc + tolerance < battery.target_final_soc_kwh:
        issues.append("terminal SOC reserve")
    return issues

def sustainability(scenario: Scenario, result: dict) -> dict:
    dt = scenario.interval_minutes / 60
    generated = sum(slot.solar_kw * dt for slot in scenario.slots)
    curtailed = result["totals"]["curtailed_kwh"]
    return {
        "solar_utilization_ratio": round((generated - curtailed) / generated, 4)
            if generated else None,
        "carbon_avoided_kg": round(
            result["baseline"]["carbon_kg"] - result["totals"]["carbon_kg"], 6
        ),
    }
