"""Interval energy balance, battery constraints and four dispatch policies."""
from __future__ import annotations
from dataclasses import asdict
from math import sqrt
from statistics import quantiles
from .models import Dispatch, Interval, Site, Summary

STRATEGIES = ("baseline", "self_consumption", "price_aware", "resilience")


def _thresholds(profile: list[Interval]) -> tuple[float, float]:
    values = sorted(x.import_eur_per_kwh for x in profile if x.grid_available)
    if not values:
        return (0.0, 0.0)
    if len(values) < 4:
        return (values[0], values[-1])
    cuts = quantiles(values, n=4, method="inclusive")
    return cuts[0], cuts[2]


def simulate(profile: list[Interval], site: Site, strategy: str = "price_aware", step_minutes: int = 15) -> tuple[Summary, list[Dispatch]]:
    if strategy not in STRATEGIES:
        raise ValueError(f"unknown strategy: {strategy}")
    if not 1 <= step_minutes <= 1440 or 1440 % step_minutes:
        raise ValueError("step_minutes must divide one day")
    if not profile:
        raise ValueError("profile must not be empty")
    from datetime import datetime, timedelta
    times = [datetime.fromisoformat(x.timestamp) for x in profile]
    if any((b-a) != timedelta(minutes=step_minutes) for a,b in zip(times,times[1:])):
        raise ValueError("timestamps must be contiguous at the configured cadence")
    dt = step_minutes / 60
    battery = site.battery
    eta = sqrt(battery.roundtrip_efficiency)
    soc = battery.initial_soc_kwh
    low, high = _thresholds(profile)
    steps: list[Dispatch] = []
    for row in profile:
        load = row.load_kw * dt
        pv = row.pv_kw * dt
        pv_to_load = min(load, pv)
        deficit = load - pv_to_load
        surplus = pv - pv_to_load
        charge = discharge = grid_in = grid_out = curtailed = shed = critical_shed = 0.0

        def take_charge(wanted: float) -> float:
            nonlocal soc, charge
            allowed = min(max(0.0, wanted), battery.charge_kw*dt-charge, (battery.max_soc_kwh-soc)/eta)
            allowed = max(0.0, allowed)
            soc += allowed * eta
            charge += allowed
            return allowed

        def take_discharge(wanted: float, floor: float) -> float:
            nonlocal soc, discharge
            allowed = min(max(0.0, wanted), battery.discharge_kw*dt-discharge, max(0.0, soc-floor)*eta)
            allowed = max(0.0, allowed)
            soc -= allowed / eta
            discharge += allowed
            return allowed

        if not row.grid_available:
            # No grid imports or exports. Preserve critical service ahead of flexible demand.
            deficit -= take_discharge(deficit, battery.min_soc_kwh)
            shed = max(0.0, deficit)
            critical_shed = max(0.0, row.load_kw*dt*site.critical_load_fraction - (load-shed))
            take_charge(surplus)
            curtailed = max(0.0, surplus-charge)
        else:
            if surplus > 0:
                if strategy != "baseline":
                    take_charge(surplus)
                remainder = surplus-charge
                grid_out = min(remainder, site.grid_export_limit_kw*dt)
                curtailed = max(0.0, remainder-grid_out)
            else:
                reserve = battery.min_soc_kwh
                if strategy == "resilience":
                    reserve = max(reserve, battery.capacity_kwh*site.resilience_reserve_fraction)
                discharge_now = strategy in ("self_consumption", "resilience") or (strategy == "price_aware" and row.import_eur_per_kwh >= high)
                if discharge_now:
                    deficit -= take_discharge(deficit, reserve)
                grid_in = min(deficit, site.grid_import_limit_kw*dt)
                deficit -= grid_in
                # Import cap must be respected even if policy prefers to hold battery.
                deficit -= take_discharge(deficit, battery.min_soc_kwh)
                shed = max(0.0, deficit)
                critical_shed = max(0.0, row.load_kw*dt*site.critical_load_fraction - (load-shed))
                if strategy == "price_aware" and row.import_eur_per_kwh <= low:
                    headroom = max(0.0, site.grid_import_limit_kw*dt-grid_in)
                    grid_charge = take_charge(headroom)
                    grid_in += grid_charge
        if not (battery.min_soc_kwh-1e-8 <= soc <= battery.max_soc_kwh+1e-8):
            raise AssertionError("SOC out of bounds")
        # AC-side conservation: PV + imports + discharge = served load + charge + exports + curtailment.
        balance = pv + grid_in + discharge - (load-shed+charge+grid_out+curtailed)
        if abs(balance) > 1e-7:
            raise AssertionError(f"energy imbalance: {balance}")
        cost = (grid_in*row.import_eur_per_kwh - grid_out*row.export_eur_per_kwh
                + (charge+discharge)*battery.degradation_eur_per_kwh)
        steps.append(Dispatch(row.timestamp, round(soc, 9), grid_in, grid_out, charge, discharge,
                              curtailed, shed, critical_shed, cost, grid_in*row.carbon_kg_per_kwh,
                              row.grid_available))
    peak = max(x.grid_import_kwh/dt for x in steps)
    energy_cost = sum(x.operating_cost_eur for x in steps)
    demand = peak*site.demand_charge_eur_per_kw
    summary = Summary(strategy, len(steps), sum(x.grid_import_kwh for x in steps),
                      sum(x.grid_export_kwh for x in steps), sum(x.battery_charge_kwh for x in steps),
                      sum(x.battery_discharge_kwh for x in steps), sum(x.pv_curtailed_kwh for x in steps),
                      sum(x.load_shed_kwh for x in steps), sum(x.critical_shed_kwh for x in steps),
                      sum(x.emissions_kg for x in steps), energy_cost, demand, energy_cost+demand,
                      peak, soc)
    return summary, steps


def compare(profile: list[Interval], site: Site, step_minutes: int = 15) -> dict[str, dict]:
    return {name: asdict(simulate(profile, site, name, step_minutes)[0]) for name in STRATEGIES}
