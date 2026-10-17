"""Mixed-integer dispatch: no simultaneous battery charging and discharging."""

from dataclasses import dataclass
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix
from .baseline import CURTAIL_PENALTY, no_storage_baseline
from .domain import Scenario

FIELDS = ("charge", "discharge", "import", "export", "curtail", "soc", "mode")

class OptimizationError(RuntimeError):
    """No proven optimal feasible schedule was found."""

@dataclass(frozen=True)
class SolverOptions:
    time_limit_seconds: float = 20.0
    relative_gap: float = 0.001

def solve(scenario: Scenario, options: SolverOptions | None = None) -> dict:
    options = options or SolverOptions()
    count = len(scenario.slots)
    dt = scenario.interval_minutes / 60
    battery, grid = scenario.battery, scenario.grid
    size, peak = 7 * count + 1, 7 * count

    def at(t: int, field: str) -> int:
        return 7 * t + FIELDS.index(field)

    c = np.zeros(size)
    lb, ub = np.zeros(size), np.full(size, np.inf)
    integer = np.zeros(size, dtype=int)
    c[peak] = grid.demand_charge_usd_per_kw
    for t, slot in enumerate(scenario.slots):
        ub[at(t, "charge")] = battery.max_charge_kw
        ub[at(t, "discharge")] = battery.max_discharge_kw
        ub[at(t, "import")] = grid.max_import_kw
        ub[at(t, "export")] = grid.max_export_kw
        ub[at(t, "curtail")] = slot.solar_kw
        lb[at(t, "soc")] = battery.min_soc_kwh
        ub[at(t, "soc")] = battery.capacity_kwh
        ub[at(t, "mode")] = 1
        integer[at(t, "mode")] = 1
        c[at(t, "charge")] = dt * battery.degradation_usd_per_kwh
        c[at(t, "discharge")] = dt * battery.degradation_usd_per_kwh
        c[at(t, "import")] = dt * (slot.import_price_usd_per_kwh
            + slot.grid_kgco2_per_kwh * grid.carbon_price_usd_per_kg)
        c[at(t, "export")] = -dt * slot.export_price_usd_per_kwh
        c[at(t, "curtail")] = dt * CURTAIL_PENALTY

    A = lil_matrix((5 * count + 1, size), dtype=float)
    row_lb = np.full(5 * count + 1, -np.inf)
    row_ub = np.full(5 * count + 1, np.inf)
    for t, slot in enumerate(scenario.slots):
        ch, dis = at(t, "charge"), at(t, "discharge")
        imp, exp = at(t, "import"), at(t, "export")
        cur, soc, mode = at(t, "curtail"), at(t, "soc"), at(t, "mode")
        A[t, imp], A[t, exp], A[t, ch], A[t, dis], A[t, cur] = 1, -1, -1, 1, -1
        row_lb[t] = row_ub[t] = slot.load_kw - slot.solar_kw
        row = count + t
        A[row, soc] = 1
        A[row, ch] = -dt * battery.charge_efficiency
        A[row, dis] = dt / battery.discharge_efficiency
        if t:
            A[row, at(t - 1, "soc")] = -1
            row_lb[row] = row_ub[row] = 0
        else:
            row_lb[row] = row_ub[row] = battery.initial_soc_kwh
        A[2 * count + t, ch] = 1
        A[2 * count + t, mode] = -battery.max_charge_kw
        row_ub[2 * count + t] = 0
        A[3 * count + t, dis] = 1
        A[3 * count + t, mode] = battery.max_discharge_kw
        row_ub[3 * count + t] = battery.max_discharge_kw
        A[4 * count + t, imp] = 1
        A[4 * count + t, peak] = -1
        row_ub[4 * count + t] = 0
    A[5 * count, at(count - 1, "soc")] = 1
    row_lb[5 * count] = battery.target_final_soc_kwh

    result = milp(c=c, integrality=integer, bounds=Bounds(lb, ub),
                  constraints=LinearConstraint(A.tocsr(), row_lb, row_ub),
                  options={"time_limit": options.time_limit_seconds,
                           "mip_rel_gap": options.relative_gap})
    if result.status != 0 or result.x is None:
        raise OptimizationError(f"dispatch failed (status={result.status}): {result.message}")

    def clean(value: float) -> float:
        return round(max(0.0, float(value)), 6)

    totals = {key: 0.0 for key in ("import_kwh", "export_kwh", "curtailed_kwh",
        "charged_kwh", "discharged_kwh", "carbon_kg", "energy_import_usd",
        "export_credit_usd", "degradation_usd", "carbon_usd", "curtail_penalty_usd")}
    schedule = []
    for t, slot in enumerate(scenario.slots):
        v = {field: clean(result.x[at(t, field)]) for field in FIELDS[:-1]}
        imp, exp, ch, dis, cur = (v[key] for key in ("import", "export", "charge", "discharge", "curtail"))
        totals["import_kwh"] += imp * dt
        totals["export_kwh"] += exp * dt
        totals["curtailed_kwh"] += cur * dt
        totals["charged_kwh"] += ch * dt
        totals["discharged_kwh"] += dis * dt
        totals["carbon_kg"] += imp * dt * slot.grid_kgco2_per_kwh
        totals["energy_import_usd"] += imp * dt * slot.import_price_usd_per_kwh
        totals["export_credit_usd"] += exp * dt * slot.export_price_usd_per_kwh
        totals["degradation_usd"] += (ch + dis) * dt * battery.degradation_usd_per_kwh
        totals["carbon_usd"] += imp * dt * slot.grid_kgco2_per_kwh * grid.carbon_price_usd_per_kg
        totals["curtail_penalty_usd"] += cur * dt * CURTAIL_PENALTY
        schedule.append(dict(timestamp=slot.timestamp.isoformat(), load_kw=slot.load_kw,
            solar_kw=slot.solar_kw, charge_kw=ch, discharge_kw=dis,
            grid_import_kw=imp, grid_export_kw=exp, solar_curtail_kw=cur, soc_kwh=v["soc"]))
    totals["peak_import_kw"] = clean(result.x[peak])
    totals["demand_charge_usd"] = totals["peak_import_kw"] * grid.demand_charge_usd_per_kw
    totals["total_cost_usd"] = (totals["energy_import_usd"] - totals["export_credit_usd"]
        + totals["degradation_usd"] + totals["carbon_usd"]
        + totals["curtail_penalty_usd"] + totals["demand_charge_usd"])
    totals = {k: round(v, 6) for k, v in totals.items()}
    baseline = no_storage_baseline(scenario)
    return dict(status="optimal", scenario_name=scenario.name,
        objective_usd=round(float(result.fun), 6),
        savings_vs_no_storage_usd=round(baseline["total_cost_usd"] - totals["total_cost_usd"], 6),
        totals=totals, baseline=baseline, schedule=schedule,
        solver={"engine": "SciPy HiGHS MILP", "status_code": int(result.status),
                "mip_gap": float(getattr(result, "mip_gap", 0.0) or 0.0)})
